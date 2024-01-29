from typing import List

from qdrant_client import QdrantClient, models
from utils import get_image_embedding, get_text_embedding


def search_text(text: str, client: QdrantClient, **kwargs) -> List[dict]:
    print("Searching for: ", text)

    # Extract the optional filters
    director = kwargs.get("director")
    actor = kwargs.get("actor")
    genre = kwargs.get("genre")
    year = kwargs.get("year")
    k = kwargs.get("k", 20)
    k = int(k)

    # Build the query filter
    if any([director, actor, genre, year]):
        query_filter = models.Filter(should=[])
        if director:
            query_filter.should.append(
                models.FieldCondition(
                    key="director[]",
                    match=models.MatchValue(value=director),
                )
            )
        if actor:
            query_filter.should.append(
                models.FieldCondition(
                    key="actor[]",
                    match=models.MatchValue(value=actor),
                )
            )
        if genre:
            query_filter.should.append(
                models.FieldCondition(
                    key="genre[]",
                    match=models.MatchValue(value=genre),
                )
            )
        if year:
            query_filter.should.append(
                models.FieldCondition(
                    key="year",
                    match=models.MatchValue(value=year),
                )
            )
    else:
        query_filter = None
    print("Query filter: ", query_filter)
    results = client.search(
        collection_name="captions",
        query_vector=get_text_embedding(text)[0].tolist(),
        query_filter=query_filter,
        limit=k,
        score_threshold=0.6
    )
    
    # Return the payloads of the extracted results 
    return results 

def search_images(image: str) -> List[str]:
    pass
