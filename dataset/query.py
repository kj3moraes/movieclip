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


def get_movie_poster_from_id(id: str):
    url = f"{BASE_URL}i={id}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {id}")
    return __process_response(r.json())


CAPTIONING_API_URL = (
    "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}


def get_image_caption(im_path: Path):
    with open(im_path, "rb") as f:
        data = f.read()
    response = requests.post(CAPTIONING_API_URL, headers=headers, data=data)
    return response.json()


# output = get_image_caption("cats.jpg")
print(get_movie_data_from_title("The Laundromat"))
