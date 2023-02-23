

# Import Segmenter class from audio_segmenter.py in the path /Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/utils/audio_segmentation.py

import sys


from audio_segmentation import Segmenter

# Create a Segmenter object
segmenter = Segmenter("/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/data/raw/video1.mp3", "/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/data/raw/video1_transcript.srt", "segment_data")

segmenter.create_segments()

#export PYTHONPATH=$PYTHONPATH:/Users/harshbhatia/Documents/CBD/Charlie_CBD/nexusbot/utils