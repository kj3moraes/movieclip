"""
This file is for downloading the entire dataset. This will require that you have an OMDb API key.
- 180,000 images 
- 3000 movies 
Approximately 15GB of data will be required for all these images. 
"""

import json
import math
import queue
import threading
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from shutil import rmtree

import requests
from bs4 import BeautifulSoup
from query import get_movie_data_from_title

# ============================= IMPORTANT CONSTANTS =============================

# Constants for the producers consumers
MAX_BUFFER_SIZE = 100
NUM_PRODUCERS = 15
NUM_CONSUMERS = 60

# Directory path
SAVE_PATH = Path("data")
TRAINING_DATA_PATH = SAVE_PATH / "train"
TESTING_DATA_PATH = SAVE_PATH / "test"
FILM_GRAB_URL = "https://film-grab.com/movies-a-z/"


# ============================= DOWNLOADING IMAGES ===============================

# Queue to hold URLS
url_queue = queue.Queue(MAX_BUFFER_SIZE)

# Semaphores for the producers consumers
queue_semaphore = threading.Semaphore(0)
full_semaphore = threading.Semaphore(MAX_BUFFER_SIZE)

# Movie results
movie_results = {}
total_movies = 0
total_images = 0
movie_results_mutex = threading.Lock()

# Map of IMDB ID to Movie name
movie_id_names = {}
movie_id_names_mutex = threading.Lock()

# Reverse Lookup of movie name to IMDB ID
movie_name_ids = {}
movie_name_ids_mutex = threading.Lock()

# Director to movie ID map
director_movie_id = defaultdict(list)
director_movie_id_mutex = threading.Lock()

# Genre to movie ID map
genre_movie_id = defaultdict(list)
genre_movie_id_mutex = threading.Lock()

# Existing movie names
# This is used to check if we have already downloaded the images ane
# metadata for a movie.
existing_movie_names = set()


def __download_images_from_url(url: str, movie_id: str) -> int:
    """
    Function to download images from a given URL and stores them in the specified path.
    Returns the number of images that were extracted.
    """

    image_count = 0

    # Get the HTML of the page from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all image elements in the page
    # 'bwg-masonry-thumb' because that is FILM-GRABs unique class name for
    # all the images that occur in that specific
    image_tags = soup.find_all(
        "img", class_="skip-lazy bwg-masonry-thumb bwg_masonry_thumb_0"
    )
    alt_images_tags = soup.find_all(
        "img", class_="skip-lazy bwg-standart_thumb_img_0"
    )
    image_tags.extend(alt_images_tags)
    movie_train_data_dir = TRAINING_DATA_PATH / movie_id
    movie_test_data_dir = TESTING_DATA_PATH / movie_id

    # Create a directory to save images
    # (NOTE): We can freely delete the directory if it already exists because 
    # if we are downloading the images here, it means that the exisiting folder
    # is corrupted or incomplete.
    if movie_train_data_dir.exists():
        rmtree(movie_train_data_dir)
    movie_train_data_dir.mkdir(parents=True)
    if movie_test_data_dir.exists():
        rmtree(movie_test_data_dir)
    movie_test_data_dir.mkdir(parents=True)

    # Download all the images and move 5 of them from
    # training set to the testing set.
    image_count = len(image_tags)
    if image_count == 0:
        raise Exception("No images found")
    
    train_img_count, test_img_count = 0, 0
    test_img_ids = set([i for i in range(0, image_count, max(1, image_count // 5))])
    for idx, img_tag in enumerate(image_tags):
        img_url = img_tag.get("src")
        if img_url:
            if idx in test_img_ids:
                img_filename = (
                    TESTING_DATA_PATH / movie_id / f"{test_img_count + 1}.jpg"
                )
                test_img_count += 1
            else:
                img_filename = (
                    TRAINING_DATA_PATH / movie_id / f"{train_img_count + 1}.jpg"
                )
                train_img_count += 1
            with open(img_filename, "wb") as img_file:
                response = requests.get(img_url)
                if response.status_code == requests.codes.ok:
                    image_data = response.content
                img_file.write(image_data)

    return image_count


def __produce(data: list):
    for url_name_pair in data:
        # Add the URL to the queue
        full_semaphore.acquire()

        # If the movie is already present in the dataset,
        # then we don't need to download it again.
        if url_name_pair[1] in existing_movie_names:
            print(f"Omitting {url_name_pair[1]} since it is already present")
            full_semaphore.release()
            continue
        url_queue.put(url_name_pair)
        print(f"Added {url_name_pair[1]} to the queue")
        queue_semaphore.release()


def __consume(save_path: Path):
    
    global total_movies
    global total_images
    
    while True:
        queue_semaphore.acquire()
        data = url_queue.get()
        full_semaphore.release()

        url, movie_name = data

        # Get the movie information from OMDb
        try:
            movie_data = get_movie_data_from_title(movie_name)
            movie_id = movie_data["imdbID"]
            directors = movie_data["Director"]
            genres = movie_data["Genre"]
        except Exception as e:
            print(f"Failed for movie {movie_name} since {e}")
            movie_name_ids[movie_name] = {
                "Error": f"Failed to get movie information because {str(e)}"
            }
            continue

        # Download images from the extracted URL
        print(f"Downloading images from {url} for {movie_name}")
        try:
            num_images = __download_images_from_url(url, movie_id)
        except Exception as e:
            print(f"Failed for movie {movie_name} because {e}")
            movie_name_ids[movie_name] = {
                "Error": f"Failed to download the images because {str(e)}"
            }
            continue

        # Only add to the results if we have successfully downloaded the images
        # and gotten the metadata.
        with movie_id_names_mutex:
            movie_id_names[movie_id] = movie_name

        with director_movie_id_mutex:
            for director in directors:
                director_movie_id[director].append(movie_id)

        with genre_movie_id_mutex:
            for genre in genres:
                genre_movie_id[genre].append(movie_id)

        with movie_results_mutex:
            movie_results[movie_id] = movie_data
            total_movies += 1
            total_images += num_images
            movie_results[movie_id]["NumImages"] = num_images

            # Checkpointing
            # - every 500 movies we save the results, genres, directors, and ids
            if len(movie_results) % 500 == 0:
                with open(save_path / "results.json", "w+") as outfile:
                    json.dump(movie_results, outfile, indent=4)

                with open(save_path / "directors.json", "w+") as outfile:
                    json.dump(director_movie_id, outfile, indent=4)

                with open(save_path / "genres.json", "w+") as outfile:
                    json.dump(genre_movie_id, outfile, indent=4)

                with open(save_path / "ids.json", "w+") as outfile:
                    json.dump(movie_id_names, outfile, indent=4)
                    
                with open(save_path / "reverse_ids.json", "w+") as outfile:
                    json.dump(movie_name_ids, outfile, indent=4)

                with open(save_path / "stats.txt", "w+") as outfile:
                    outfile.write(f"Total movies = {total_movies}\n")
                    outfile.write(f"Total images = {total_images}\n")
                
                print(f"\n========Checkpointed at {len(movie_results)} movies========\n")
        url_queue.task_done()


def collect_existing_movies():
    """
    Function to collect all the existing movies that are present in the dataset.
    This must be CALLED ONLY WHEN YOU KNOW THAT THE DATASET IS PRESENT.
    """

    global existing_movie_names
    global movie_results
    global genre_movie_id
    global director_movie_id
    global movie_id_names
    global movie_name_ids

    existing_movie_ids = set()
    for movie_id in TRAINING_DATA_PATH.iterdir():
        if movie_id.is_dir():
            existing_movie_ids.add(movie_id.name)

    # Read the ids.json file
    with open(SAVE_PATH / "ids.json", "r") as infile:
        movie_id_names = json.load(infile)

    for movie_id in existing_movie_ids:
        if movie_id in movie_id_names:  
            existing_movie_names.add(movie_id_names[movie_id])
    
    # Populate the results, genres, directors
    with open(SAVE_PATH / "results.json", "r") as infile:
        movie_results.update(json.load(infile))
    with open(SAVE_PATH / "genres.json", "r") as infile:
        genre_movie_id.update(json.load(infile))
    with open(SAVE_PATH / "directors.json", "r") as infile:
        director_movie_id.update(json.load(infile))
    with open(SAVE_PATH / "reverse_ids.json", "r") as infile:
        movie_name_ids.update(json.load(infile))
    with open(SAVE_PATH / "ids.json", "r") as infile:
        movie_id_names.update(json.load(infile))


def download_images() -> dict:
    """
    Function to extract HTMLS links from a list and and download the images from
    the respective webpages. (Modifies global variables)

    Returns a dictionary containing information about the movies downloaded and the
    path to where they are downloaded.
    """

    # Get the HTML content from the URL
    fp = urllib.request.urlopen(FILM_GRAB_URL)
    html_bytes = fp.read()
    html_content = html_bytes.decode("utf8")
    fp.close()
    soup = BeautifulSoup(html_content, "html.parser")

    if SAVE_PATH.exists():
        collect_existing_movies()
    else:
        SAVE_PATH.mkdir(exist_ok=True)
        TRAINING_DATA_PATH.mkdir(exist_ok=True)
        TESTING_DATA_PATH.mkdir(exist_ok=True)

    # Find all list items with class 'listing-item'
    listing_items = soup.find_all("li", class_="listing-item")
    urls = []
    # Loop through each listing item
    for item in listing_items:
        link = item.find("a", class_="title")
        if link:
            # Extract the URL and text of the link
            url = link.get("href")
            name = link.get_text()
            urls.append((url, name))
    if DEMO:
        urls = urls[:8]
    print(f"Total number of movies = {len(urls)}")
    CHUNK_SIZE = int(math.ceil(len(urls) / NUM_PRODUCERS))
    chunked_urls = [
        urls[i : min(len(urls), i + CHUNK_SIZE)]
        for i in range(0, len(urls), CHUNK_SIZE)
    ]

    # Create producer threads
    producer_threads = []
    for i in range(NUM_PRODUCERS):
        producer = threading.Thread(target=__produce, args=(chunked_urls[i],))
        producer_threads.append(producer)
        producer.start()

    # Create consumer threads
    consumer_threads = []
    for i in range(NUM_CONSUMERS):
        consumer = threading.Thread(target=__consume, args=(SAVE_PATH,))
        consumer_threads.append(consumer)
        consumer.start()

    # Wait for all producer threads to complete
    for producer in producer_threads:
        producer.join()

    # Wait for all tasks in the queue to be processed
    url_queue.join()


#  =========================== SAVING ALL THE NECESSARY INFORMATION ===========================

DEMO = False 

print("Starting to download all images")
download_images()
print("Completed downloading all images")

# Save the movie results, movie ids maps, directors, and genres.
with open(SAVE_PATH / "results.json", "w+") as outfile:
    json.dump(movie_results, outfile, indent=4)
    total_movies = len(movie_results)
    total_images = sum([movie["NumImages"] for movie in movie_results.values()])

with open(SAVE_PATH / "directors.json", "w+") as outfile:
    json.dump(director_movie_id, outfile, indent=4)

with open(SAVE_PATH / "genres.json", "w+") as outfile:
    json.dump(genre_movie_id, outfile, indent=4)

with open(SAVE_PATH / "ids.json", "w+") as outfile:
    json.dump(movie_id_names, outfile, indent=4)
    
with open(SAVE_PATH / "reverse_ids.json", "w+") as outfile:
    json.dump(movie_name_ids, outfile, indent=4)

with open(SAVE_PATH / "stats.txt", "w+") as outfile:
    outfile.write(f"Total movies = {total_movies}\n")
    outfile.write(f"Total images = {total_images}\n")

print(f"Completed saving information to {SAVE_PATH}")
