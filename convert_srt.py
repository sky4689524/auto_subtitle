import re
from transformers import MarianMTModel, MarianTokenizer
import argparse
import requests

# Function to get available models from Hugging Face model hub.
def get_available_models():
	url = "https://huggingface.co/api/models?search=Helsinki-NLP%2Fopus-mt"
	response = requests.get(url)
	models = response.json()
	model_names = [model["modelId"] for model in models]
	return model_names

# Function to get the appropriate Marian model name for the given source and target languages.
def get_marian_model_name(src_language, tgt_language, model_size, available_models):
	big_model_name_pattern = f"Helsinki-NLP/opus-mt-tc-big-{src_language}-{tgt_language}"
	regular_model_name_pattern = f"Helsinki-NLP/opus-mt-{src_language}-{tgt_language}"
	
	if model_size == "big":
		# Search for a big-sized model first
		for model_name in available_models:
			if big_model_name_pattern in model_name:
				return model_name
		
		# If a big-sized model is not found, search for a regular-sized model
		for model_name in available_models:
			if regular_model_name_pattern in model_name:
				return model_name
	else:
		# Search for a regular-sized model
		for model_name in available_models:
			if regular_model_name_pattern in model_name:
				return model_name

	raise ValueError(f"No model found for {src_language}-{tgt_language} with size {model_size}")

# Function to translate a subtitle using the given tokenizer and model.
def translate_subtitle(subtitle: str, tokenizer, model):
	model_inputs = tokenizer(subtitle, return_tensors="pt", padding=True)
	translated_tokens = model.generate(**model_inputs, max_new_tokens=50)
	return tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

# Function to parse command-line arguments.
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input_srt", required=True, help="input srt file")
	parser.add_argument("-o", "--output_file", required=False, default = "./video/transcription_convert.srt", help="output converted srt file path")
	parser.add_argument("--input_language", required=True, help="the language of input transcripton srt file (e.g., 'en' for English, 'de' for German)")
	parser.add_argument("--output_language", required=True, help="the language of output transcription srt file (e.g., 'en' for English, 'de' for German)")
	parser.add_argument("--model_size", required=False, default = "big", help="the language model size (regular or big). The big size model has better quality but much slower")

	args = parser.parse_args()

	return args

if __name__ == "__main__":
	namespace = parse_args()

	input_srt_file = namespace.input_srt
	output_srt_file = namespace.output_file
	input_language = namespace.input_language
	output_language = namespace.output_language
	model_size = namespace.model_size

	# Get available models
	available_models = get_available_models()

	# Get the model name based on the input and output languages
	model_name = get_marian_model_name(input_language, output_language, model_size, available_models)

	# Load tokenizer and model
	tokenizer = MarianTokenizer.from_pretrained(model_name)
	model = MarianMTModel.from_pretrained(model_name)

	with open(input_srt_file, "r", encoding="utf-8") as f:
		content = f.read()

	# Regular expression pattern for matching subtitles with their timecodes and text.
	subtitle_pattern = re.compile(r"(\d+)\n((?:\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n)+)((?:(?!^\d+\n).)*)(?:\n|$)", re.MULTILINE)
	subtitles = subtitle_pattern.findall(content)

	# Open the output file and write the translated subtitles.
	with open(output_srt_file, "w", encoding="utf-8") as f:
		for subtitle in subtitles:
			index, timecode, text = subtitle
			# Translate the subtitle text.
			translated_text = translate_subtitle(text.strip(), tokenizer, model)
			# Write the translated subtitle to the output file.
			f.write(f"{index}\n{timecode}{translated_text}\n\n")
