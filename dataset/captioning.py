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
import sys
import base64
import json
import queue
import threading
from pathlib import Path

import tqdm
from query import get_images_caption

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
    """This function captions all the images of a directory.
    It reads each one and places them in an array. The whole array is captioned and
    then saved in a JSON file.
    """

    images = {} 
    caption_file_path = dir_path / "captions.json"
    if caption_file_path.exists():
        return

    # Read all the images of the directory
    for image_path in tqdm.tqdm(dir_path.iterdir(), desc=f"Captioning {dir_path.name}"):
        if image_path.is_file() and image_path.suffix == ".jpg":
            with open(image_path, "rb") as image_file:
                image_file_name = image_path.name.split(".")[0] 
                images[image_file_name] = base64.b64encode(image_file.read()).decode("utf-8")

    # Get the captions of the images
    try:
        captions = get_images_caption(images)
        print("Captions are ", captions)
    except Exception as e:
        print(f"Failed to caption images of {dir_path.name}")
        print(e)
        return

    # Save the captions to a JSON file.
    with open(caption_file_path, "w") as caption_file_path:
        json.dump(captions, caption_file_path)

def caption_images():
    """This function captions all the images in the dataset.
    For each directory, it will create a captions.json file that contains the captions for each image
    of that directory.
    """
    for dir_path in TRAINING_DATA_PATH.iterdir():
        if dir_path.is_dir():
            __caption_images_of_dir(dir_path)

    for dir_path in TESTING_DATA_PATH.iterdir():
        if dir_path.is_dir():
            __caption_images_of_dir(dir_path)


if __name__ == "__main__":
    path_to_img_dir = sys.argv[1]
    __caption_images_of_dir(Path(path_to_img_dir))
