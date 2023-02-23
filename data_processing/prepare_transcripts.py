if __name__ == '__main__':
    # Modify it to use parallel processing
    import os
    from multiprocessing import Pool
    from stt import transcribe_audio

    # Define input and output directories
    input_dir = "/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/data/raw"
    output_dir = "/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/data/raw"

    # Create a pool of processes
    pool = Pool(processes=4)

    # Loop through all files in input directory and transcribe them
    for file in os.listdir(input_dir):
        if file.endswith(".mp3") and not os.path.exists(os.path.join(output_dir, file.split(".")[0] + "_transcript.srt")):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.split(".")[0] + ".srt")
            pool.apply_async(transcribe_audio, args=("small", input_path, output_path))

    # Close the pool
    pool.close()

    # Wait for all processes to finish
    pool.join()