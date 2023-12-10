import os
import requests 
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def get_movie_data_from_title(title: str):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {title}")
    return r.json()


def get_movie_poster_from_id(id: str):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={id}"

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(f"Failed to get data for {title}")
    return r.json()

