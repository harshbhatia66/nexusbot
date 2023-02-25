import os
from speaker_verification import SpeakerVerification
import tempfile

if __name__ == '__main__':
    # Load the models
    reference_file = "/Users/harshbhatia/Documents/nexusbot/training/standard.wav"
    folder_path = "/Users/harshbhatia/Documents/data/training"
    metadata_db_path = "metadata.db"
    spk_verify = SpeakerVerification(reference_file, folder_path, metadata_db_path)
    # Check for similarity
    temp_dir = tempfile.gettempdir()
    # Iterate through all the files in the folder and check for similarity with reference audio file
    spk_verify.verify(temp_dir)
    # Commit the changes to the database and close the connection
    spk_verify.close_connection()

