#!/bin/bash

# Parse arguments
youtube_url=""
balance=""
balance_provided=false
while [[ $# -gt 0 ]]; do
  case $1 in
    -y)
      youtube_url="$2"
      shift 2
      ;;
    -b)
      balance_provided=true
      if [[ -n $2 && $2 != -* ]]; then
        balance="$2"
        shift 2
      else
        balance="0.2"
        shift 1
      fi
      ;;
    *)
      echo "Invalid option: $1"
      exit 1
      ;;
  esac
done

# Validate balance option if provided
if [ -n "$balance" ] && ! [[ "$balance" =~ ^0(\.[0-9]+)?$|^1(\.0+)?$ ]]; then
  echo "Invalid balance value: $balance. It should be a number between 0.0 and 1.0."
  exit 1
fi

# Remove the existing output file if it exists
if [ -f "output.mp4" ]; then
    rm "output.mp4"
fi

if [ -f "downloaded_audio.mp3" ]; then
    rm "downloaded_audio.mp3"
fi

# Create a temporary directory to hold the remuxed video files
temp_dir=$(mktemp -d)
echo "Temporary directory created: $temp_dir"

# Remux all video files to a common format and codec
video_files=$(ls *.{mp4,mkv,avi,flv,wmv,mov,webm} 2>/dev/null | sort)
echo "Found video files: $video_files"
for file in $video_files; do
  output_file="$temp_dir/$(basename "$file" .${file##*.}).mp4"
  echo "Remuxing video file: $file to $output_file"
  ffmpeg -i "$file" -c:v copy -c:a copy "$output_file"
done

# Create a temporary file to hold the list of remuxed video files
video_temp_file=$(mktemp)
echo "Temporary file for video list created: $video_temp_file"
for file in $(ls "$temp_dir"/*.mp4 | sort); do
  echo "file '$file'" >> $video_temp_file
done

# Combine the videos using ffmpeg
echo "Combining videos..."
ffmpeg -f concat -safe 0 -i $video_temp_file -c copy combined_video.mp4

# Download audio from YouTube if URL is provided
if [ -n "$youtube_url" ]; then
  yt-dlp -f bestaudio -o "downloaded_audio.%(ext)s" "$youtube_url"
  downloaded_file=$(ls downloaded_audio.* | head -n 1)
  mv "$downloaded_file" "downloaded_audio.mp3"
  audio_file="downloaded_audio.mp3"
else
  # Find the first audio file in the current directory
  audio_files=$(ls *.{mp3,wav,aac,flac} 2>/dev/null | sort)
  echo "Found audio files: $audio_files"
  if [ -n "$audio_files" ]; then
    audio_file=$(echo "$audio_files" | head -n 1)
    echo "Using audio file: $audio_file"
  else
    echo "No audio files found."
    audio_file=""
  fi
fi

# Add the audio file to the output video if available
if [ -n "$audio_file" ]; then
  if ! $balance_provided; then
    # No balance provided, replace the video audio with the downloaded audio
    ffmpeg -i combined_video.mp4 -i "$audio_file" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -fflags +genpts output.mp4
  else
    # Balance provided, mix the audio and video
    ffmpeg -i combined_video.mp4 -i "$audio_file" -filter_complex "[1:a]volume=${balance}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2" -c:v copy -c:a aac -shortest -fflags +genpts output.mp4
  fi
else
  # No audio file found, just rename the combined video
  mv combined_video.mp4 output.mp4
fi

# Clean up the temporary files and directory
echo "Cleaning up temporary files..."
rm $video_temp_file
rm -r $temp_dir
rm -f downloaded_audio.mp3
rm -f combined_video.mp4

# Check if VLC is installed and open the output video
if command -v vlc >/dev/null 2>&1; then
  echo "Opening output video with VLC..."
  vlc output.mp4 >/dev/null 2>&1 &
else
  echo "VLC is not installed."
fi