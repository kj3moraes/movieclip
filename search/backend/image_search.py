from typing import List

from PIL import Image
from qdrant_client import QdrantClient, models

from utils import get_image_embedding, get_text_embedding


def search_text_in_db(text: str, client: QdrantClient, **kwargs) -> List[dict]:
    """Semantically searches the vector store's "captions" collection for images
        whose captions match the parameter `text`

    Args:
        text (str): caption to be searched for.
        client (QdrantClient): vector store

    Returns:
        List[dict]: the closest points
    """

    # Extract the optional filters
    director = kwargs.get("director")
    movie = kwargs.get("movie")
    actor = kwargs.get("actor")
    genre = kwargs.get("genre")
    year = kwargs.get("year")
    k = kwargs.get("k", 20)
    k = int(k)

    # Build the query filter
    if any([movie, director, actor, genre, year]):
        query_filter = models.Filter(must=[])
        if movie:
            query_filter.must.append(
                models.FieldCondition(
                    key="title",
                    match=models.MatchValue(value=movie),
                )
            )
        if director:
            query_filter.must.append(
                models.FieldCondition(
                    key="director[]",
                    match=models.MatchValue(value=director),
                )
            )
        if actor:
            query_filter.must.append(
                models.FieldCondition(
                    key="actor[]",
                    match=models.MatchValue(value=actor),
                )
            )
        if genre:
            query_filter.must.append(
                models.FieldCondition(
                    key="genre[]",
                    match=models.MatchValue(value=genre),
                )
            )
        if year:
            query_filter.must.append(
                models.FieldCondition(
                    key="year",
                    match=models.MatchValue(value=year),
                )
            )
    else:
        query_filter = None
    results = client.search(
        collection_name="captions",
        query_vector=get_text_embedding(text)[0].tolist(),
        query_filter=query_filter,
        limit=k,
    )

    return [result.model_dump() for result in results]


def search_images_in_db(image: Image, client: QdrantClient) -> List[dict]:
    """Semantically searches the vector store's "scenes" collection for images like
        the parameter `image`

    Args:
        image (Image): image to be semantically searched
        client (QdrantClient): vector store

    Returns:
        List[dict]: the closest points
    """

    results = client.search(
        collection_name="scenes", query_vector=get_image_embedding(image)[0].tolist()
    )

    return [result.model_dump() for result in results]
