import whisper
import torch
from whisper.utils import WriteSRT
import os
from multiprocessing import Pool

def transcribe_audio(model_name: str, file_path: str, output_dir: str):
    model = whisper.load_model(model_name)
    model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    file_name = file_path.split("/")[-1].split(".")[0] + '_transcript.srt'
    print(f"Starting {file_name}")
    result = model.transcribe(file_path, fp16=False, language='English')
    writer = WriteSRT(output_dir)
    with open(file_name, "w") as f:
        writer.write_result(result, f)
        
