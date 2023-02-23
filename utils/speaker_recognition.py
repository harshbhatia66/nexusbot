import os
import torch
from speechbrain.pretrained import SpeakerRecognition
from speechbrain.pretrained import EncoderClassifier
from speechbrain.pretrained import Pretrained
import sqlite3
import tempfile
import re
from natsort import natsorted

class SpeakerVerification:
    def __init__(self, reference_file, folder_path, metadata_db_path):
        self.reference_file = reference_file
        self.folder_path = folder_path
        self.metadata_db_path = metadata_db_path

        self.sr_model, self.ec_model, self.p_model = self.load_models()
        self.emb_ref = self.extract_embeddings(self.p_model, self.ec_model, self.reference_file)
        self.conn, self.c = self.create_metadata_table(self.metadata_db_path)

    def load_models(self):
        # Load the speaker recognition model
        sr_model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

        # Load the encoder classifier model
        ec_model = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

        p_model = Pretrained.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
        return sr_model, ec_model, p_model

    def extract_embeddings(self, p_model, ec_model, reference_file):
        # Extract the embeddings of the reference audio file
        waveform_x = p_model.load_audio(path=reference_file)
        batch_x = waveform_x.unsqueeze(0)
        emb_ref = ec_model.encode_batch(batch_x, normalize=True)
        return emb_ref

    def compare_embeddings(self, emb_ref, emb_y):
        similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
        score = similarity(emb_y, emb_ref)
        is_speaker = 1 if score > 0.25 else 0
        return is_speaker

    def create_metadata_table(self, metadata_db_path):
        # Connect to the SQLite database
        conn = sqlite3.connect(metadata_db_path)
        c = conn.cursor()

        # Create the table for storing metadata
        c.execute('''CREATE TABLE IF NOT EXISTS speaker_files
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, is_speaker INTEGER)''')
        return conn, c

    def verify(self, temp_dir):
        count_fail = 0
        # Loop through all the files in the folder and check for similarity with reference audio file
        for file in natsorted(os.listdir(self.folder_path), key=lambda x: (x.split("")[0], int(x.split("")[1].split(".")[0][7:]))):
            if file.endswith('.wav'):
                waveform_y = self.p_model.load_audio(path=os.path.join(self.folder_path, file), savedir=temp_dir)
                batch_y = waveform_y.unsqueeze(0)
                emb_y = self.ec_model.encode_batch(batch_y, normalize=True)
                is_speaker = self.compare_embeddings(self.emb_ref, emb_y)
                if is_speaker == 0:
                    count_fail += 1
                print(f"File: {file} Passes Verification: {is_speaker}")
                # Insert the metadata into the database
                self.c.execute("INSERT INTO speaker_files (file_path, is_speaker) VALUES (?, ?)", (os.path.join(self.folder_path, file), is_speaker))

                os.remove(os.path.join(temp_dir, file))

    def close_connection(self):
        # Commit the changes to the database and close the connection
        self.conn.commit()
        self.conn.close()

# Usage
# # Load the models
# reference_file = "/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/data/training/standard.wav"
# folder_path = "/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/tests/segment_data"
# metadata_db_path = "/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/tests/metadata.db"
# spk_verify = SpeakerVerification(reference_file, folder_path, metadata_db_path)
# # Check for similarity
# temp_dir = tempfile.gettempdir()
# spk_verify.verify(temp_dir)
# # Commit the changes to the database and close the connection
# spk_verify.close_connection()