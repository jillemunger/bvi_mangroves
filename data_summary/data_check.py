import os
import wave
import pandas as pd

# Specify the root directory
root_directory = r"/Volumes/SeaBABELa/BVI Mangroves_2024/raw/Round 2"

# Initialize lists to collect data for each subfolder
data = []

# Traverse each subfolder
for folder_name in os.listdir(root_directory):
    subfolder_path = os.path.join(root_directory, folder_name)
    
    # Check if it's a directory
    if os.path.isdir(subfolder_path):
        wav_file_count = 0
        zero_byte_wav_count = 0
        total_size_wav = 0
        total_duration_wav = 0
        
        # Use os.walk() to traverse through subdirectories and files
        for dirpath, dirnames, filenames in os.walk(subfolder_path):
            for file_name in filenames:
                file_path = os.path.join(dirpath, file_name)
                
                # Check if it's a file and a WAV audio file
                if os.path.isfile(file_path) and file_path.lower().endswith('.wav'):
                    file_size = os.path.getsize(file_path)
                    
                    if file_size > 0:
                        wav_file_count += 1
                        total_size_wav += file_size
                        
                        # Try to read the WAV file for duration
                        try:
                            with wave.open(file_path, 'rb') as audio_file:
                                frames = audio_file.getnframes()
                                rate = audio_file.getframerate()
                                duration = frames / float(rate)
                                total_duration_wav += duration
                        except wave.Error as e:
                            print(f"Skipping {file_name}: {e}")
                        except Exception as e:
                            print(f"An unexpected error occurred while reading {file_name}: {e}")
                    else:
                        zero_byte_wav_count += 1
        
        # Append subfolder data to the list
        data.append([folder_name, wav_file_count, zero_byte_wav_count, total_size_wav / (1024 * 1024), total_duration_wav])  # Size in MB

# Summarize the total number, size, and duration of all subdirectories for .wav files
total_wav_files = sum(row[1] for row in data)
total_zero_byte_wav_files = sum(row[2] for row in data)
total_size_wav_mb = round(sum(row[3] for row in data), 2)
total_duration_wav_sec = round(sum(row[4] for row in data), 2)

# Append the overall totals to the data list
data.append(["Total", total_wav_files, total_zero_byte_wav_files, total_size_wav_mb, total_duration_wav_sec])

# Create a DataFrame and export to CSV
df = pd.DataFrame(data, columns=["Subfolder", "Number of .wav Files > 0 bytes", "Number of 0 Byte .wav Files", "Total Size (MB)", "Total Duration (seconds)"])
output_csv = r"/Volumes/SeaBABELa/BVI Mangroves_2024/HansA_round2_summary.csv"  # Set the output path for the CSV file
df.to_csv(output_csv, index=False)

print(f"Summary saved to: {output_csv}")
