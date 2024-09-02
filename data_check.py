"""
This script analyzes the contents of subdirectories within a specified root directory.
It performs the following tasks for each subfolder:
1. Counts the number of files that are greater than 0 bytes.
2. Counts the number of files that are exactly 0 bytes.
3. Calculates the total size of files (in megabytes) that are greater than 0 bytes.
4. Calculates the total duration (in seconds) of valid WAV audio files that are greater than 0 bytes.
5. Summarizes the total number, size, and duration for all subdirectories.
6. Exports the results to a CSV file with the summary for each subfolder and the overall totals.

Output:
- A CSV file named 'summary.csv' containing the statistics for each subfolder and overall totals.

Note:
- The script handles exceptions for invalid or corrupted WAV files and skips them.
- It uses the 'pandas' library for creating and exporting the summary to a CSV file.
"""

import os
import wave
import pandas as pd

# Specify the root directory
root_directory = r"E:\BVI Mangroves_2024\raw\Round 1"

# Initialize lists to collect data for each subfolder
data = []

# Traverse each subfolder
for folder_name in os.listdir(root_directory):
    subfolder_path = os.path.join(root_directory, folder_name)
    
    # Check if it's a directory
    if os.path.isdir(subfolder_path):
        file_count = 0
        zero_byte_count = 0
        total_size = 0
        total_duration = 0
        
        # Traverse each file in the subfolder
        for file_name in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, file_name)
            
            # Check if it's a file and not hidden
            if os.path.isfile(file_path) and not file_name.startswith('._'):
                file_size = os.path.getsize(file_path)
                
                if file_size > 0:
                    file_count += 1
                    total_size += file_size
                    
                    # Check if the file is a WAV audio file
                    if file_path.lower().endswith('.wav'):
                        try:
                            with wave.open(file_path, 'rb') as audio_file:
                                frames = audio_file.getnframes()
                                rate = audio_file.getframerate()
                                duration = frames / float(rate)
                                total_duration += duration
                        except wave.Error as e:
                            print(f"Skipping {file_name}: {e}")
                        except Exception as e:
                            print(f"An unexpected error occurred while reading {file_name}: {e}")
                else:
                    zero_byte_count += 1
        
        # Append subfolder data to the list
        data.append([folder_name, file_count, zero_byte_count, total_size / (1024 * 1024), total_duration])  # Size in MB

# Summarize the total number, size, and duration of all subdirectories
total_files = sum(row[1] for row in data)
total_zero_byte_files = sum(row[2] for row in data)
total_size_mb = round(sum(row[3] for row in data), 2)
total_duration_sec = round(sum(row[4] for row in data), 2)

# Append the overall totals to the data list
data.append(["Total", total_files, total_zero_byte_files, total_size_mb, total_duration_sec])

# Create a DataFrame and export to CSV
df = pd.DataFrame(data, columns=["Subfolder", "Number of Files > 0 bytes", "Number of 0 Byte Files", "Total Size (MB)", "Total Duration (seconds)"])
output_csv = r"E:\BVI Mangroves_2024\round1_summary.csv"  # Set the output path for the CSV file
df.to_csv(output_csv, index=False)

print(f"Summary saved to: {output_csv}")
