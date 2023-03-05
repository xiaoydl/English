import argparse
import json
import re
import sys
from google.cloud import texttospeech_v1beta1 as texttospeech
import os

POST_PATH = r'..\_posts'
AUDIO_PATH = r'..\audio'

def generate_voice(txt_file: str):
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(os.curdir) + "\google_TTS_key.json"
	# Instantiates a client
	client = texttospeech.TextToSpeechClient()

	# read txt file
	with open(txt_file, 'r', encoding='utf-8') as f:
		txt = f.read()
	
	if txt_file.endswith('.md'):
		txt = re.sub('^.*---.*---', '', txt, flags=re.S).strip()
	

	# Set the text input to be synthesized
	synthesis_input = texttospeech.SynthesisInput(ssml=txt)

	# Build the voice request, select the language code ("en-US") and the ssml
	# voice gender ("neutral")
	voice = texttospeech.VoiceSelectionParams(
		language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
		name='en-US-Wavenet-F'
	)

	# Select the type of audio file you want returned
	audio_config = texttospeech.AudioConfig(
		audio_encoding=texttospeech.AudioEncoding.MP3
	)

	request = texttospeech.SynthesizeSpeechRequest(
		input=synthesis_input,
		voice=voice,
		audio_config=audio_config,
		enable_time_pointing=[texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK])

	# Perform the text-to-speech request on the text input with the selected
	# voice parameters and audio file type
	response = client.synthesize_speech(request)

	# The response's audio_content is binary.
	file_name = os.path.splitext(os.path.basename(txt_file))[0]
	voice_file = f'{AUDIO_PATH}\{file_name}.mp3'
	with open(voice_file, "wb") as out:
		# Write the response to the output file.
		out.write(response.audio_content)
		print(f'Audio content written to file {voice_file}')

	voice_timestamp_file = f'{AUDIO_PATH}\{file_name}.json'
	with open(voice_timestamp_file, "w") as out:
		marks = [dict(sec=t.time_seconds, name=t.mark_name)
				for t in response.timepoints]
		# Write timepoints to the output file.
		json.dump(marks, out)
		print(f'time points written to file {voice_timestamp_file}')

def get_post_file_path(file_name):
	if not file_name:
		return None
	file_dir = os.path.dirname(os.path.realpath(__file__))
	print(file_dir)
	file_name = file_name if file_name.lower().endswith('.md') else file_name + '.md'
	file_path = os.path.join(file_dir, f'{POST_PATH}\{file_name}')
	print(f'{file_path}')
	if not os.path.exists(file_path):
		return None
	return file_path

if __name__ == '__main__':

	if len(sys.argv) > 1:
		f_path = get_post_file_path(sys.argv[1])
		if f_path:
			generate_voice(f_path)
		else:
			print(f'file {f_path} does not exist')
	else:
		print('no post named specified...')