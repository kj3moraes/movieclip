import os
import requests 
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&"

def __process_respose(response: dict) -> dict:
    """
    Function takes a response from OMDb and converts into a dictionary that we want
    """
    pass

def get_movie_data_from_title(title: str):
    url = f"{BASE_URL}t={title}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {title}")
    return r.json()


def get_movie_poster_from_id(id: str):
    url = f"{BASE_URL}i={id}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {title}")
    return r.json()

