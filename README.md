# Auto Subtitle

This repository provides tools to transcribe videos and create subtitles using Python. Additionally, you can convert subtitles from one language to another. The provided video player can play videos and display subtitles, or you can use your preferred video player.

As a bonus, a script is included to download YouTube videos using the command line.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. **youtube_downloader.py**: Download YouTube videos in the best quality MP4 format.

```bash
python youtube_downloader.py --video_url https://www.youtube.com/video_url/ --output_folder path/to/output
```

2. **video_to_srt.py**: Transcribe video to create an SRT (SubRip Subtitle) file.

```bash
python video_to_srt.py --input_video path/to/video --output_file path/to/output.srt --language "language code"
```

This script uses the Google Speech Recognition API, which supports a wide range of languages and language variants. You can find a list of supported languages and their respective codes in the [official documentation](https://cloud.google.com/speech-to-text/docs/languages).

3. **convert_srt.py**: Convert subtitles to another language.

```bash
python convert_srt.py --input_srt path/to/original_srt.srt --output_file path/to/output.srt --input_language "original srt language" --output_language "output srt language"
```

This script uses the Hugging Face Transformers API to convert subtitles. You can find the list of available translation models on [this page](https://huggingface.co/models?pipeline_tag=translation&search=Helsinki-NLP%2Fopus-mt).

4. **video_player.py**: Play a video and its subtitles in a custom video player.

```bash
python video_player.py --input_video path/to/video.mp4 --input_srt path/to/srt.srt
```

This custom video player, built with wxPython and the VLC module, can play videos and display subtitles. You can control the playback using play, pause, forward, backward, and time bar controls. The video player icons are from https://www.flaticon.com/.

## Note

Python version: 3.8.16

In order to run this project successfully, you need to have PyTorch installed, as the `MarianMTModel` from the `transformers` library relies on it. The recommended version is `torch-2.0.0` with `cuda11.7`, but you should verify the appropriate PyTorch version for your system by consulting the [official documentation](https://pytorch.org/get-started/locally/).

This project utilizes various video and audio libraries, such as `moviepy`, `python-vlc`, and `pydub`. To ensure seamless functionality, you may need to install FFmpeg, which is a dependency for `moviepy` to perform certain video and audio encoding/decoding operations. Follow the instructions below to install FFmpeg on your operating system:

* **Windows**: Download the FFmpeg executable from the official website: https://ffmpeg.org/download.html and add it to your system's PATH.
* **macOS**: Use Homebrew to install FFmpeg by running the command `brew install ffmpeg`.
* **Ubuntu or other Debian-based systems**: Use apt to install FFmpeg with the command `sudo apt install ffmpeg`.

After completing the FFmpeg installation, the libraries should be able to process video and audio files without any issues..