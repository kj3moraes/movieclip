from qdrant_client import QdrantClient
from typing import List
from utils import get_image_embedding, get_text_embedding


def search_text(text: str, k: int, client: QdrantClient) -> List[str]:
    print("Searching for: ", text)
    results = client.search(
        collection_name="captions",
        query_vector=get_text_embedding(text)[0].tolist(),
        limit=k,
    )
    return results


def search_images(image: str) -> List[str]:
    pass 