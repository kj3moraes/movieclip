"""
This file is for captioning each of the images that are present in the dataset directory. You must have 
the dataset downloaded in the data/ directory. You will need a HuggingFace Token. 
The dataset must be structured as follows:

|- data/
|   |- train/
|   |   |- <movie_id>/
|   |       |- 1.jpeg
|   |       |- 2.jpeg
|   |       ...
|   |- genres.json
|   |- results.json
|   |- ids.json
|   |- directors.json
"""

import os
import queue
import threading
from pathlib import Path

import tqdm
from query import get_image_caption

# ============================= IMPORTANT CONSTANTS =============================

# Constants for the producers consumers
MAX_BUFFER_SIZE = 50
NUM_PRODUCERS = 5
NUM_CONSUMERS = 20

# Data path
DATASET_PATH = Path("./data")
TRAINING_DATA_PATH = DATASET_PATH / "train"
TESTING_DATA_PATH = DATASET_PATH / "test"


def __caption_images_of_dir(dir_path: Path):
    """ This function captions all the images of a directory.
        It reads each one and s"""



def caption_images():
    """ This function captions all the images in the dataset. 
        For each directory, it will create a captions.json file that contains the captions for each image
        of that directory.
    """
    for dir_path in TRAINING_DATA_PATH.iterdir():
        if dir_path.is_dir():
            __caption_images_of_dir(dir_path)
        
    for dir_path in TESTING_DATA_PATH.iterdir():
        if dir_path.is_dir():
            __caption_images_of_dir(dir_path)
