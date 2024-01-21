import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&"


def __process_response(response: dict) -> dict:
    """
    Function takes a response from OMDb and converts into a dictionary that we want
    """

    response["Director"] = response.get("Director", "").replace(", ", ",").split(",")
    response["Writer"] = response.get("Writer", "").replace(", ", ",").split(",")
    response["Actors"] = response.get("Actors", "").replace(", ", ",").split(",")
    response["Genre"] = response.get("Genre", "").replace(", ", ",").split(",")
    return response


def get_movie_data_from_title(title: str):
    url = f"{BASE_URL}t={title}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {title}")
    return __process_response(r.json())


def get_movie_data_from_id(id: str):
    url = f"{BASE_URL}i={id}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {id}")
    return __process_response(r.json())


def get_movie_poster_from_id(id: str):
    url = f"{BASE_URL}i={id}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {id}")
    return __process_response(r.json())


CAPTIONING_IMAGE_URL = os.getenv("CAPTIONING_IMAGE_URL")
HUGGINGFACE_HUB_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
headers = {"Authorization": f"Bearer {HUGGINGFACE_HUB_TOKEN}"}


def get_image_caption(im_data: str, image_name: str):
    """Generates a caption for a single image

    Args:
        im_data (str): base64 encoded image
        image_name (str): name of the image

    Raises:
        Exception: Failed to caption image

    Returns:
        dict: caption of the image
    """
    payload = {
        "inputs": {image_name: im_data},
        "parameters": {
            "do_sample": True,
            "top_p": 0.9,
            "min_length": 5,
            "max_length": 40,
        },
    }
    response = requests.post(CAPTIONING_IMAGE_URL, headers=headers, json=payload)
    if response.status_code != requests.codes.ok:
        raise Exception("Failed to caption image")

    caption = response.json()["captions"][0]
    return caption
