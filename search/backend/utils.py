import uuid

from PIL import Image
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("openai/clip-vit-base-patch16")
processor = AutoImageProcessor.from_pretrained("openai/clip-vit-base-patch16")
tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch16")


def generate_id(file_name: str, movie_id: str):
    """
    Generates a UUID based on the combination of two input strings.
    """
    combined_string = file_name + movie_id
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, combined_string))


def get_image_embedding(image: Image):
    """Generates the image embeddings for an image and returns
        it as a numpy array

    Args:
        image (Image): image to be embedded

    Returns:
        array of floats.
    """
    inputs = processor(images=[image], return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    return outputs.detach().numpy()


def get_text_embedding(text: str):
    """Generates the text embeddings for an caption and returns
        it as a numpy array

    Args:
        text (str): caption to be embedded

    Returns:
        array of floats.
    """
    inputs = tokenizer([text], return_tensors="pt")
    outputs = model.get_text_features(**inputs)
    return outputs.detach().numpy()
