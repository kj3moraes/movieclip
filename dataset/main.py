from pathlib import Path
from shutil import rmtree
import os
import json
import math
from dotenv import load_dotenv
import requests
from collections import defaultdict

import urllib.request 
import urllib.parse
from bs4 import BeautifulSoup

import threading
import queue

from query import get_movie_data_from_title


# ============================= IMPORTANT CONSTANTS =============================

# Constants for the producers consumers  
MAX_BUFFER_SIZE = 100
NUM_PRODUCERS = 10
NUM_CONSUMERS = 50

# Directory path
SAVE_PATH = Path("data")
TRAINING_DATA_PATH = SAVE_PATH / "train"
TESTING_DATA_PATH  = SAVE_PATH / "test"
FILM_GRAB_URL = "https://film-grab.com/movies-a-z/"


# ============================= DOWNLOADING IMAGES ===============================

# Queue to hold URLS
url_queue = queue.Queue(MAX_BUFFER_SIZE)
# Mutex to protect access to the queue
url_queue_mutex = threading.Lock()

# Semaphores for the producers consumers
queue_semaphore = threading.Semaphore(0)
full_semaphore = threading.Semaphore(MAX_BUFFER_SIZE)

# Movie results 
movie_results = {}
movie_results_mutex = threading.Lock()

# Map of IMDB ID to Movie name
movie_id_names = {} 
movie_id_names_mutex = threading.Lock()

# Director to movie ID map
director_movie_id = defaultdict(list)
director_movie_id_mutex = threading.Lock()

# Genre to movie ID map
genre_movie_id = defaultdict(list) 
genre_movie_id_mutex =  threading.Lock()


def __download_images_from_url(url: str, movie_id: str) -> int: 
    """
    Function to download images from a given URL and stores them in the specified path.
    Returns the number of images that were extracted.
    """
    
    image_count = 0 
    
    # Get the HTML of the page from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image elements in the page
    # 'bwg-masonry-thumb' because that is FILM-GRABs unique class name for
    # all the images that occur in that specific  
    image_tags = soup.find_all('img', class_='bwg-masonry-thumb')
    movie_train_data_dir= TRAINING_DATA_PATH / movie_id 
    movie_test_data_dir = TESTING_DATA_PATH / movie_id 

    # Create a directory to save images
    if movie_train_data_dir.exists():
        rmtree(movie_train_data_dir)
    movie_train_data_dir.mkdir(parents=True)
    if movie_test_data_dir.exists():
        rmtree(movie_test_data_dir)
    movie_test_data_dir.mkdir(parents=True)


    # Download all the images and move 5 of them from 
    # training set to the testing set.
    image_count = len(image_tags)
    train_img_count, test_img_count = 0, 0
    test_img_ids = set([i for i in range(0, image_count, image_count // 5)])
    for idx, img_tag in enumerate(image_tags):
        img_url = img_tag.get('src')
        if img_url:
            if idx in test_img_ids:
                img_filename = TESTING_DATA_PATH / movie_id / f"{test_img_count + 1}.jpg"
                test_img_count += 1
            else:
                img_filename = TRAINING_DATA_PATH / movie_id / f"{train_img_count + 1}.jpg"
                train_img_count += 1
            with open(img_filename, 'wb') as img_file:
                response = requests.get(img_url)
                if response.status_code == requests.codes.ok:
                    image_data = response.content
                img_file.write(image_data)

    return image_count


def __produce(urls: list):
    for url in urls:
        # Add the URL to the queue
        full_semaphore.acquire()
        url_queue.put(url)
        print(f"Added {url} to the queue")
        queue_semaphore.release()
    

def __consume(save_path: Path):
    while True:
        queue_semaphore.acquire()
        data = url_queue.get()
        full_semaphore.release()

        url, movie_name = data

        # Get the movie information from OMDb
        movie_data = get_movie_data_from_title(movie_name) 
        try:
            movie_id = movie_data['imdbID']
            directors = movie_data['Director']
            genres = movie_data['Genre']
        except Exception as e:
            print(f"Failed for movie {movie_name} since {e}") 
            continue
        
        # We must make this before because
        with movie_results_mutex:
            movie_results[movie_name] = movie_data
    
        # Download images from the extracted URL
        print(f"Downloading images from {url} for {movie_name}")
        try:
            num_images = __download_images_from_url(url, movie_id) 
        except Exception as e:
            print(f"Failed for movie {movie_name} becaue {e}")
            continue

        with movie_results_mutex:    
            movie_results[movie_name]['num_images'] = num_images 

        with movie_id_names_mutex:
            movie_id_names[movie_id] = movie_name 

        with director_movie_id_mutex:
            for director in directors:
                director_movie_id[director].append(movie_id)
                
        with genre_movie_id_mutex:
            for genre in genres:
                genre_movie_id[genre].append(movie_id)

        url_queue.task_done()


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
    soup = BeautifulSoup(html_content, 'html.parser')

    SAVE_PATH.mkdir(exist_ok=True)
    TRAINING_DATA_PATH.mkdir(exist_ok=True)
    TESTING_DATA_PATH.mkdir(exist_ok=True)

    # Find all list items with class 'listing-item'
    listing_items = soup.find_all('li', class_='listing-item')
    urls = [] 
    # Loop through each listing item
    for item in listing_items:
        link = item.find('a', class_='title')
        if link:
            # Extract the URL and text of the link
            url = link.get('href')
            text = link.get_text()
            urls.append((url, text))
    if DEMO:
        urls = urls[:4]
    print(f"Total number of movies = {len(urls)}")
    CHUNK_SIZE = int(math.ceil(len(urls) / NUM_PRODUCERS))
    chunked_urls = [urls[i:min(len(urls), i+CHUNK_SIZE)] for i in range(0, len(urls), CHUNK_SIZE)] 

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

with open(SAVE_PATH / "directors.json", "w+") as outfile:
    json.dump(director_movie_id, outfile, indent=4)

with open(SAVE_PATH / "genres.json", "w+") as outfile:
    json.dump(genre_movie_id, outfile, indent=4)

with open(SAVE_PATH / "ids.json", "w+") as outfile:
    json.dump(movie_id_names, outfile, indent=4)

print(f"Completed saving information to {SAVE_PATH}")