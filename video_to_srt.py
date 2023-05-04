import os
import argparse
import tempfile
import textwrap
import nltk
from io import BytesIO

import speech_recognition as sr
from pydub import AudioSegment, silence
from moviepy.editor import *
import numpy as np
import pysrt

from tqdm import tqdm

# This function parses command-line arguments using the argparse module, taking input_video, output_file, and language as arguments.
# The input_video is the input video file path, output_file is the path for the output SRT file, and language is the language code for transcription.
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input_video", required=True, help="input video file")
	parser.add_argument("-o", "--output_file", required=False, default = "./video/transcription.srt", help="output srt file path")
	parser.add_argument("-l", "--language", required=False, default="en-US", help="language code for transcription (e.g., 'en-US' for English, 'de-DE' for German)")

	args = parser.parse_args()

	return args

# This function takes a text input and splits it into separate sentences using the Natural Language Toolkit (nltk).
# It returns a list of sentences.
def split_sentences(text):
	return nltk.sent_tokenize(text)

# This function processes SRT subtitles by splitting individual subtitles containing multiple sentences
# into separate subtitles for each sentence, adjusting their start and end times accordingly.
# It takes a list of input SubRipItems (subs) and returns a list of new SubRipItems (new_subs) with the processed sentences.
def process_srt_subs(subs):
	# Initialize an empty list to store the new subtitles.
	new_subs = []

	# Iterate through each subtitle in the input list (subs).
	for sub in subs:
		# Use the split_sentences function to split the subtitle's text into individual sentences.
		sentences = split_sentences(sub.text)
		# Get the number of sentences in the subtitle.
		num_sentences = len(sentences)

		# Check if there's more than one sentence in the subtitle.
		if num_sentences > 1:
			# Calculate the duration of the subtitle by subtracting the start time from the end time.
			duration_delta = sub.end - sub.start
			# Calculate the duration of each sentence by dividing the total duration by the number of sentences.
			# Convert the resulting seconds and milliseconds into a SubRipTime object.
			sentence_duration = pysrt.SubRipTime(0, 0, duration_delta.seconds / num_sentences, int(duration_delta.milliseconds / num_sentences))

			# Iterate through each sentence in the list of sentences.
			for i, sentence in enumerate(sentences):
				# Create a new SubRipItem object with the same index, start, end, and text as the original subtitle.
				new_sub = pysrt.SubRipItem(index=sub.index, start=sub.start, end=sub.end, text=sub.text)
				# Update the start time of the new subtitle by adding the sentence_duration multiplied by the index of the sentence.
				new_sub.start = sub.start + pysrt.SubRipTime(0, 0, sentence_duration.seconds * i, sentence_duration.milliseconds * i)
				# Update the end time of the new subtitle by adding the sentence_duration to its start time.
				new_sub.end = new_sub.start + sentence_duration
				# Set the text of the new subtitle to the current sentence.
				new_sub.text = sentence
				# Append the new subtitle to the list of new subtitles.
				new_subs.append(new_sub)
		else:
			# If there's only one sentence in the subtitle, append the subtitle to the list of new subtitles as-is.
			new_subs.append(sub)

	# Return the list of new subtitles.
	return new_subs

# This function takes a NumPy array representing audio data and converts it into an AudioSegment object.
# The input audio_array is a 1D array containing the audio samples, frame_rate is the sample rate of the audio data (default 48000),
# sample_width is the number of bytes per sample (default 2), and channels is the number of audio channels (default 1).
def numpy_array_to_audio_segment(audio_array, frame_rate=48000, sample_width=2, channels=1):
	audio_array = (audio_array * np.iinfo(np.int16).max).astype(np.int16)
	byte_data = audio_array.tobytes()

	with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
		tmp_file.write(b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00')
		tmp_file.write(frame_rate.to_bytes(4, 'little'))
		tmp_file.write((frame_rate * sample_width).to_bytes(4, 'little'))
		tmp_file.write((sample_width).to_bytes(2, 'little') + b'\x10\x00data')
		tmp_file.write(len(byte_data).to_bytes(4, 'little') + byte_data)
		tmp_file.flush()

		audio_segment = AudioSegment.from_file(tmp_file.name, format="wav")

	return audio_segment

# This function takes a time value in seconds and converts it into a formatted string representation suitable for SRT files.
# The formatted string follows the pattern HH:MM:SS,000, where HH is hours, MM is minutes, and SS is seconds.
def format_time(seconds):
	hours, remainder = divmod(seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},000"

# This function transcribes the given audio_data using Google Speech Recognition and the specified language.
# It returns the transcribed text as a string. If the transcription is unsuccessful, it returns an empty string.
def transcribe_audio(audio_data, language):
	try:
		text = recognizer.recognize_google(audio_data, language=language)
	except sr.UnknownValueError:
		text = ""
	except sr.RequestError as e:
		print(f"Error: {e}")
		text = ""
	return text

# This function takes a text input and splits it into smaller chunks based on the maximum line width (max_width) and maximum number of lines per chunk (max_lines).
# It uses the textwrap module to wrap the text and returns a list of lists, where each sublist contains the lines of a chunk.
def split_text_into_chunks(text, max_width=40, max_lines=2):
	wrapped_text = textwrap.fill(text, width=max_width)
	split_text = wrapped_text.split('\n')
	return [split_text[i:i + max_lines] for i in range(0, len(split_text), max_lines)]

if __name__ == "__main__":

	namespace = parse_args()

	input_video = namespace.input_video
	output_file = namespace.output_file
	language = namespace.language

	output_folder = os.path.dirname(output_file)

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	# Load the input video and extract the audio samples
	video = VideoFileClip(input_video)
	samples = video.audio.to_soundarray(fps=48000)
	audio_array = samples.mean(axis=1)
	audio = numpy_array_to_audio_segment(audio_array, frame_rate=48000)

	# Detect non-silent segments of the audio
	silence_points = silence.detect_nonsilent(audio, min_silence_len=300, silence_thresh=-40)

	recognizer = sr.Recognizer()

	transcribed_text = []

	# Transcribe the non-silent segments of the audio
	for index, (start_time, end_time) in enumerate(tqdm(silence_points, desc="Transcribing audio", ncols=100)):
		start_time = start_time / 1000
		end_time = end_time / 1000
		duration = end_time - start_time

		# Convert the audio segment to a WAV file
		audio_data = audio[start_time * 1000:end_time * 1000].export(format="wav")
		
		# Transcribe the audio segment
		with sr.AudioFile(audio_data) as source:
			audio_data = recognizer.record(source)
			text = transcribe_audio(audio_data, language)
			chunks = split_text_into_chunks(text)

			total_words = len(text.split())
			if total_words == 0:
				continue

			for chunk in chunks:
				chunk_duration = duration * (len(' '.join(chunk).split()) / total_words)
				transcribed_text.append((start_time, start_time + chunk_duration, chunk))
				start_time += chunk_duration

	# Write the transcribed text to an SRT file
	with open(output_file, "w", encoding="utf-8") as srt_file:
		index = 1
		for i, (start_time, end_time, lines) in enumerate(transcribed_text):
			if i + 1 < len(transcribed_text):
				end_time = transcribed_text[i + 1][0]
			srt_file.write(f"{index}\n")
			srt_file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
			srt_file.write('\n'.join(lines) + "\n\n")
			index += 1

	print("Transcription completed.")

	# Load the generated SRT file
	subs = pysrt.open(output_file, encoding="utf-8")
	
	# Process the SRT subtitles to split sentences
	processed_subs = process_srt_subs(subs)

	# Save the processed subtitles to the output SRT file
	output_subs = pysrt.SubRipFile(items=processed_subs)
	output_subs.save(output_file)

	print("Post-processing completed.")
   
