import os
import subprocess
import argparse

def parse_args():
	# Set up command line argument parser
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--video_url", required=True, help="youtube video url")
	parser.add_argument("-o", "--output_folder", required=False, default="./video", help="output folder path")

	# Parse command line arguments
	args = parser.parse_args()

	return args

def download_youtube_video(url, output_path):
	try:
		# Define the output file template
		output_file = os.path.join(output_path, "%(title)s.%(ext)s")

		# Download the video using yt-dlp
		command = [
			"yt-dlp",
			"-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
			"--merge-output-format", "mp4",
			"--output", output_file,
			url
		]

		# Run the command and check for errors
		subprocess.run(command, check=True)
		print("Download completed.")

	except subprocess.CalledProcessError as e:
		print("Error:", str(e))

if __name__ == "__main__":
	# Parse command line arguments
	namespace = parse_args()

	# Get the video URL and output folder from command line arguments
	video_url = namespace.video_url
	output_folder = namespace.output_folder

	# Create the output folder if it doesn't exist
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	# Download the YouTube video
	download_youtube_video(video_url, output_folder)
