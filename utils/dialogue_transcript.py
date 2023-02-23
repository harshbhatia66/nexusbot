import sqlite3

def create_transcripts(metadata_db_file, transcripts_dir):
    # Connect to the metadata database file
    conn = sqlite3.connect(metadata_db_file)
    c = conn.cursor()
    
    # Select all the rows from the speaker_files table
    c.execute("SELECT * FROM speaker_files")
    rows = c.fetchall()
    
    # Loop through each row in the table
    current_speaker = None
    speaker_prefix = ""
    speaker_text = ""
    current_video = None
    for row in rows:
        # Get the file path and the is_speaker value
        file_path = row[1]
        is_speaker = row[2]
        
        # Split the file path into parts
        parts = file_path.split("/")
        
        # Get the file name
        file_name = parts[-1]
        
        # Split the file name into parts
        parts = file_name.split(".")
        
        # Get the base file name (without the extension)
        base_file_name = parts[0]
        
        # Split the base file name into parts
        parts = base_file_name.split("_")
        
        # Get the video number and segment number
        video_number = int(parts[0].replace("video", ""))
        segment_number = int(parts[1].replace("segment", ""))
        
        # Create the text file path
        text_file_path = "/".join(file_path.split("/")[:-1]) + "/" + base_file_name + ".txt"
        
        # Read the text file
        with open(text_file_path, "r") as f:
            text = f.read()
        
        # If the current speaker has changed, write the previous speaker's text to the transcript file
        if current_speaker is not None and current_speaker != is_speaker:
            transcript_file_path = f"{transcripts_dir}/video{current_video}_dialogue_transcript.txt"
            with open(transcript_file_path, "a") as f:
                f.write(speaker_prefix + speaker_text + "\n")
            
            # Reset the speaker text
            speaker_text = ""
        
        # Add the speaker and text to the transcript
        if is_speaker:
            speaker_prefix = "[Speaker]: "
        else:
            speaker_prefix = "[Context]: "
        
        # Update the current speaker and speaker text
        current_speaker = is_speaker
        speaker_text
        speaker_text += text + " "
        current_video = video_number
    
    # Write the last speaker's text to the transcript file
    transcript_file_path = f"{transcripts_dir}/video{current_video}_dialogue_transcript.txt"
    with open(transcript_file_path, "a") as f:
        f.write(speaker_prefix + speaker_text + "\n")
    
    # Close the connection to the database
    conn.close()

# Example usage
# metadata_db_file = "metadata.db"
# transcripts_dir = "dialogue_transcripts"
# create_transcripts(metadata_db_file, transcripts_dir)
