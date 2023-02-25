import sqlite3


def connect_to_database(database_file):
    """Connects to the specified SQLite database file, and returns a connection and a cursor object."""
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    return conn, c


def get_speaker_files(cursor):
    """Retrieves all rows from the 'speaker_files' table, and returns the rows as a list of tuples."""
    cursor.execute("SELECT * FROM speaker_files")
    rows = cursor.fetchall()
    return rows


def extract_file_information(file_path):
    """Given a file path, extracts the file name, base file name, video number, and segment number."""
    parts = file_path.split("/")
    file_name = parts[-1]
    parts = file_name.split(".")
    base_file_name = parts[0]
    parts = base_file_name.split("_")
    video_number = int(parts[0].replace("video", ""))
    segment_number = int(parts[1].replace("segment", ""))
    return file_name, base_file_name, video_number, segment_number


def read_text_from_file(text_file_path):
    """Given a file path, reads the text from the file and returns it as a string."""
    with open(text_file_path, "r") as f:
        text = f.read()
    return text


def create_transcripts(metadata_db_file, transcripts_dir):
    """Creates transcripts for the videos, based on the data in the specified SQLite database file."""
    conn, c = connect_to_database(metadata_db_file)
    rows = get_speaker_files(c)

    current_speaker = None
    speaker_prefix = ""
    speaker_text = ""
    current_video = None
    
    for row in rows:
        file_path = row[1]
        is_speaker = row[2]

        file_name, base_file_name, video_number, segment_number = extract_file_information(file_path)
        text_file_path = "/".join(file_path.split("/")[:-1]) + "/" + base_file_name + ".txt"
        text = read_text_from_file(text_file_path)
        
        # update current_video at the start of the loop
        if current_video is None or current_video != video_number:
            if current_video is not None:
                transcript_file_path = f"{transcripts_dir}/video{current_video}_dialogue_transcript.txt"
                with open(transcript_file_path, "a") as f:
                    f.write(speaker_prefix + speaker_text + "\n")
            current_speaker = None
            speaker_prefix = ""
            speaker_text = ""
            current_video = video_number
        
        if current_speaker is not None and current_speaker != is_speaker:
            transcript_file_path = f"{transcripts_dir}/video{current_video}_dialogue_transcript.txt"
            with open(transcript_file_path, "a") as f:
                f.write(speaker_prefix + speaker_text + "\n")
            speaker_text = ""

        if is_speaker:
            speaker_prefix = "[Speaker]: "
        else:
            speaker_prefix = "[Context]: "
        
        current_speaker = is_speaker
        speaker_text += text + " "

    # Write the last speaker's text to the transcript file
    transcript_file_path = f"{transcripts_dir}/video{current_video}_dialogue_transcript.txt"
    with open(transcript_file_path, "a") as f:
        f.write(speaker_prefix + speaker_text + "\n")

    conn.close()

    

   
