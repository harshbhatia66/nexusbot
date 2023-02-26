import os
import torch
from speechbrain.pretrained import SpeakerRecognition
from speechbrain.pretrained import EncoderClassifier
from speechbrain.pretrained import Pretrained
import sqlite3
import tempfile
import re
from natsort import natsorted
import concurrent.futures

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
        """
        Structure of the metadata database:
        CREATE TABLE speaker_files (
            id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL,
            is_speaker INTEGER NOT NULL
            );
        """
        # Connect to the SQLite database
        conn = sqlite3.connect(metadata_db_path)
        c = conn.cursor()

        # Create the table for storing metadata
        c.execute('''CREATE TABLE IF NOT EXISTS speaker_files
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, is_speaker INTEGER)''')
        return conn, c

    def mac_directory_sort(lst):
        regex = re.compile(r'(\d+|\D+)')
        def key_func(s):
            return [int(n) if n.isdigit() else n.lower() for n in regex.findall(s)]
        return natsorted(lst, key=key_func)

    def verify(self, temp_dir):
        # Loop through folders in self.folder_path
        for folder in natsorted(os.listdir(self.folder_path)):
            if folder == ".DS_Store":  # skip hidden macOS files
                continue
            # Loop through files in each folder
            
            for file in natsorted(os.listdir(os.path.join(self.folder_path, folder))):
                try: 
                    if file.endswith('.wav'):
                        waveform_y = self.p_model.load_audio(path=os.path.join(self.folder_path, folder, file), savedir=temp_dir)
                        batch_y = waveform_y.unsqueeze(0)
                        emb_y = self.ec_model.encode_batch(batch_y, normalize=True)
                        is_speaker = self.compare_embeddings(self.emb_ref, emb_y)
                        
                        # Insert the metadata into the database
                        self.c.execute("INSERT INTO speaker_files (file_path, is_speaker) VALUES (?, ?)", (os.path.join(self.folder_path, folder, file), is_speaker))
            
                        os.remove(os.path.join(temp_dir, file)) 
                except Exception as e:
                    print(f"Error verifying video: {folder}")
                    # Insert the metadata into the database as invalid
                    self.c.execute("INSERT INTO speaker_files (file_path, is_speaker) VALUES (?, ?)", (os.path.join(self.folder_path, folder, file), 0))
                    
            # Print finished verifiying folder
            print(f"Finished verifying video: {folder}")
        
            

    def close_connection(self):
        # Commit the changes to the database and close the connection
        self.conn.commit()
        self.conn.close()

