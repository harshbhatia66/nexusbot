import os
import concurrent.futures
from stt import transcribe_audio

if __name__ == '__main__':
    # Define input and output directories
    input_dir = "/Users/harshbhatia/Documents/data/raw"
    output_dir = "/Users/harshbhatia/Documents/data/raw"

    # Create a list of file paths to process
    files_to_process = [
        os.path.join(input_dir, file)
        for file in os.listdir(input_dir)
        if file.endswith(".mp3")
        and not os.path.exists(os.path.join(output_dir, file.split(".")[0] + "_transcript.srt"))
    ]

    # Process the files in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
        executor.map(transcribe_audio, ["small"] * len(files_to_process), files_to_process, [output_dir] * len(files_to_process))
