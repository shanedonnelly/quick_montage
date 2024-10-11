#!/bin/bash

# Create a temporary directory to hold the remuxed video files
temp_dir=$(mktemp -d)

# Remux all video files to a common format and codec
for file in $(ls *.{mp4,mkv,avi,flv,wmv,mov,webm} 2>/dev/null | sort); do
  ffmpeg -i "$file" -c:v copy -c:a copy "$temp_dir/$(basename "$file" .${file##*.}).mp4"
done

# Create a temporary file to hold the list of remuxed video files
video_temp_file=$(mktemp)

# List all remuxed video files in the temporary directory in alphabetical order and write to the temp file
for file in $(ls "$temp_dir"/*.mp4 | sort); do
  echo "file '$file'" >> $video_temp_file
done

# Combine the videos using ffmpeg
ffmpeg -f concat -safe 0 -i $video_temp_file -c copy output.mp4

# Clean up the temporary files and directory
rm -r $temp_dir
rm $video_temp_file