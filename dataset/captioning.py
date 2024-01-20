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

import math
import sys
import base64
import json
from typing import List
import threading
from pathlib import Path

import tqdm
from query import get_image_caption

# ============================= IMPORTANT CONSTANTS =============================

# Multithreading constants
NUM_THREADS = 20

# Data path
DATASET_PATH = Path("./data")
TRAINING_DATA_PATH = DATASET_PATH / "train"
TESTING_DATA_PATH = DATASET_PATH / "test"


def __caption_images_of_dir(dir_path: Path):
    """This function captions all the images of a directory.
    It reads each one and places them in an array. The whole array is captioned and
    then saved in a JSON file.
    """

    caption_file_path = dir_path / "captions.json"
    # If the caption file already exists, remove it and create a new one
    if caption_file_path.exists():
        # Read the file
        with open(caption_file_path, "r") as caption_file:
            captions = json.load(caption_file)
        if len(captions.keys()) == len(list(dir_path.iterdir())):
            return # Captions already exist and are complete
    
    # Read all the images of the directory
    captions = {}
    for image_path in tqdm.tqdm(dir_path.iterdir(), desc=f"Captioning {dir_path.name}"):
        if image_path.is_file() and image_path.suffix == ".jpg":
            with open(image_path, "rb") as image_file:
                image_file_name = image_path.name.split(".")[0]
                image_file_ext = image_path.name.split(".")[1]
                image_data = base64.b64encode(image_file.read()).decode("utf-8")

            # Get the captions of the images
            try:
                captions[f"{image_file_name}.{image_file_ext}"] = get_image_caption(
                    image_data, image_file_name
                )
            except Exception as e:
                print(f"Failed to caption image {image_file_name} of {dir_path.name}")
                print(e)
                continue

    # Save the captions to a JSON file only if there are captions
    if captions != {}:
        with open(caption_file_path, "w") as caption_file_path:
            json.dump(captions, caption_file_path, indent=4)


def __caption_images_from_list(dir_list: List[Path]):
    for dir_path in dir_list:
        __caption_images_of_dir(dir_path)


def caption_images(dataset_split: str):
    """This function captions all the images in the dataset.
    For each directory, it will create a captions.json file that contains the captions for each image
    of that directory.
    """

    directories = []
    if dataset_split == "train":
        for dir_path in TRAINING_DATA_PATH.iterdir():
            if dir_path.is_dir():
                directories.append(dir_path)
    else:
        for dir_path in TESTING_DATA_PATH.iterdir():
            if dir_path.is_dir():
                directories.append(dir_path)

    # Multithreading
    print(f"Total number of directories = {len(directories)}")
    if DEMO:
        directories = directories[:20]
    CHUNK_SIZE = int(math.ceil(len(directories) / NUM_THREADS))
    chunked_dirs = [
        directories[i : min(len(directories), i + CHUNK_SIZE)]
        for i in range(0, len(directories), CHUNK_SIZE)
    ]

    for i in range(NUM_THREADS):
        thread = threading.Thread(
            target=__caption_images_from_list, args=(chunked_dirs[i],)
        )
        thread.start()

    for i in range(NUM_THREADS):
        thread.join()

DEMO = False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python captioning.py <train|test>")
        sys.exit(1)

    caption_images(sys.argv[1])
    
