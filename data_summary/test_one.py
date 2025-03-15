import os

# Specify the directory you want to check
subdirectory = r"/Volumes/SeaBABELa/BVI Mangroves_2024/raw/Round 3/6863_HLSCC_B_R3"

# Initialize a counter for non-zero byte .wav files
non_zero_wav_count = 0

# Traverse the subdirectory
for dirpath, dirnames, filenames in os.walk(subdirectory):
    for file_name in filenames:
        file_path = os.path.join(dirpath, file_name)
        
        # Check if the file ends with '.wav' and its size is greater than 0 bytes
        if file_path.lower().endswith('.wav') and os.path.getsize(file_path) > 0:
            non_zero_wav_count += 1

# Print the result
print(f"Number of non-zero byte .wav files: {non_zero_wav_count}")
