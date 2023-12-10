from pathlib import Path
import math
import requests
import urllib.request
import urllib.parse
from shutil import rmtree
from bs4 import BeautifulSoup

import threading
import queue

# Constants for the producers consumers  
MAX_BUFFER_SIZE = 20
NUM_PRODUCERS = 5
NUM_CONSUMERS = 20 

# Queue to hold URLS
url_queue = queue.Queue(MAX_BUFFER_SIZE)
# Mutex to protect access to the queue
url_queue_mutex = threading.Lock()

# Semaphores for the producers consumers
queue_semaphore = threading.Semaphore(0)
full_semaphore = threading.Semaphore(MAX_BUFFER_SIZE)

movie_results = {}
movie_results_mutex = threading.Lock()


def __download_images(url, directory: Path) -> int: 
    """
    Function to download images from a given URL and stores them in the specified path.
    Returns the number of images that were extracted.
    """

    print(f"Started downloading images for {url}")

    image_count = 0 
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image elements in the page
    # 'bwg-masonry-thumb' because that is FILM-GRABs unique class name for
    # all the images that occur in that specific  
    image_tags = soup.find_all('img', class_='bwg-masonry-thumb')
    
    # Create a directory to save images
    if directory.exists():
        rmtree(directory)
    directory.mkdir(parents=True)

    # Download each image
    for idx, img_tag in enumerate(image_tags):
        img_url = img_tag.get('src')
        if img_url:
            img_filename = directory / f"{idx + 1}.jpg"
            with open(img_filename, 'wb') as img_file:
                img_data = requests.get(img_url).content
                img_file.write(img_data)
                print(f"Downloaded: {img_filename}")
                image_count += 1

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
        directory_name = movie_name.strip().replace(' ', '_')

        # Download images from the extracted URL
        print(f"Downloading images from: {url} for {movie_name}")
        movie_dir_save = save_path / directory_name
        num_images = __download_images(url, movie_dir_save) 
                
        with movie_results_mutex:
            movie_results[movie_name] = {"path": movie_dir_save, "num_images": num_images}
        url_queue.task_done()


def download(url: str, save_dir: str) -> dict:
    """
    Function to extract HTMLS links from a list and and download the images from
    the respective webpages. 
    Returns a dictionary containing information about the movies downloaded and the 
    path to where they are downloaded.
    """
 
    # Get the HTML content from the URL
    fp = urllib.request.urlopen(url)
    html_bytes = fp.read()
    html_content = html_bytes.decode("utf8")
    fp.close() 
    soup = BeautifulSoup(html_content, 'html.parser')

    DIRECTORY_SAVE_PATH = Path(save_dir)
    DIRECTORY_SAVE_PATH.mkdir(exist_ok=True)

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
        consumer = threading.Thread(target=__consume, args=(DIRECTORY_SAVE_PATH,))
        consumer_threads.append(consumer)
        consumer.start()

    # Wait for all producer threads to complete
    for producer in producer_threads:
        producer.join()

    # Wait for all tasks in the queue to be processed
    url_queue.join()
