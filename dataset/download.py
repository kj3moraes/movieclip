from pathlib import Path
import requests
import urllib.request
import urllib.parse
from shutil import rmtree
from bs4 import BeautifulSoup

# Function to download images from a given URL
def download_images(url, directory: Path):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image elements in the page
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
                print("Img url is :", img_url)
                img_data = requests.get(img_url).content
                img_file.write(img_data)
                print(f"Downloaded: {img_filename}")


# Function to extract links from HTML and download images
def extract_links_and_download(url: str, save_dir: str):
    
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
    
    # Loop through each listing item
    for item in listing_items:
        link = item.find('a', class_='title')
        if link:
            # Extract the URL and text of the link
            url = link.get('href')
            text = link.get_text()
            # Replace any invalid characters in the directory name
            directory_name = ''.join(c for c in text if c.isalnum() or c.isspace())
            directory_name = directory_name.strip().replace(' ', '_')

            # Download images from the extracted URL
            print(f"Downloading images from: {url}")
            movie_dir_save = DIRECTORY_SAVE_PATH / directory_name
            download_images(url, movie_dir_save) 
        