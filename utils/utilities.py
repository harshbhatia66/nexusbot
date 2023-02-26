import os
import os
import shutil
import sqlite3

def organize_files_by_video(train_folder):
    """Organizes the files in a train folder into subfolders for each video.

    Files are expected to have the format 'video<video_num>segment<segment_num>.<ext>'.
    Subfolders are created for each video in the train folder, and all files for each
    video are moved into its respective subfolder.

    Args:
        train_folder (str): The path to the train folder to be organized.

    Returns:
        None.
    """
    # Get a list of all the files in the train folder
    files = os.listdir(train_folder)

    # Create a dictionary to hold the filenames for each video
    video_files = {}
    for file in files:
        try:
            video_num, segment_num, ext = file.split('.')
            video_name = f'video{video_num}'
            if video_name not in video_files:
                video_files[video_name] = []
            video_files[video_name].append(file)
        except ValueError:
            # Ignore files that don't have the expected format
            pass

    # Create a subfolder for each video and move the files into their respective folders
    for video_name, files in video_files.items():
        video_folder = os.path.join(train_folder, video_name)
        os.makedirs(video_folder, exist_ok=True)
        for file in files:
            src_path = os.path.join(train_folder, file)
            dst_path = os.path.join(video_folder, file)
            os.rename(src_path, dst_path)



def move_context_files(metadata_db_file, output_dir):
    """Moves all the .wav and .txt files that don't contain speech from a speaker to a new directory."""
    conn = sqlite3.connect(metadata_db_file)
    c = conn.cursor()

    # Select all the rows from the speaker_files table with is_speaker = 0
    c.execute("SELECT * FROM speaker_files WHERE is_speaker = 0")
    rows = c.fetchall()

    # Loop through each row in the table
    for row in rows:
        # Get the file path
        file_path = row[1]

        # Move the corresponding .wav file to the output directory
        wav_file_path = file_path
        if not wav_file_path.endswith(".wav"):
            wav_file_path += ".wav"
        if os.path.exists(wav_file_path):
            output_wav_path = os.path.join(output_dir, os.path.basename(wav_file_path))
            shutil.move(wav_file_path, output_wav_path)

        # Move the corresponding .txt file to the output directory
        txt_file_path = os.path.splitext(file_path)[0] + ".txt"
        if os.path.exists(txt_file_path):
            output_txt_path = os.path.join(output_dir, os.path.basename(txt_file_path))
            shutil.move(txt_file_path, output_txt_path)

    # Close the connection to the database
    conn.close()
