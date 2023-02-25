import os
from audio_segmentation import Segmenter

def main(input_dir, output_dir):
    # Make sure input directory and output directory exist
    if not os.path.exists(input_dir):
        raise Exception("Input directory does not exist")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate over audio files in input directory
    for audio_filename in os.listdir(input_dir):
        if audio_filename.endswith(".mp3"):
            audio_filepath = os.path.join(input_dir, audio_filename)
            transcript_filepath = os.path.join(input_dir, audio_filename.split(".")[0] + "_transcript.srt")
            
            # Initialize Segmenter object
            segmenter = Segmenter(audio_filepath, transcript_filepath, output_dir)

            # Create segments
            segmenter.create_segments()
            print(f"Created segments for {audio_filename}")

if __name__ == '__main__':
    # Define input and output directories
    input_dir = "/Users/harshbhatia/Documents/data/raw"
    output_dir = "/Users/harshbhatia/Documents/data/training"

    main(input_dir, output_dir)