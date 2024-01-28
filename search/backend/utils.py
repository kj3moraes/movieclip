import uuid
from pathlib import Path

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


def get_image_embedding(image_path: Path):
    image = Image.open(image_path)
    inputs = processor(images=[image], return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    return outputs.detach().numpy()


def get_text_embedding(text: str):
    inputs = tokenizer([text], return_tensors="pt")
    outputs = model.get_text_features(**inputs)
    return outputs.detach().numpy()
