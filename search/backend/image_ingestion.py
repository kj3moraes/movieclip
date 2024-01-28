import json
from hashlib import sha256
from pathlib import Path

from qdrant_client import QdrantClient, models

from utils import generate_id, get_image_embedding, get_text_embedding


def ingest_dir(dir_path: Path, client: QdrantClient, movie_info: dict):
    print("Processing ", dir_path)
    with open(dir_path / "captions.json") as f:
        captions = json.load(f)

    movie_id = dir_path.name
    scene_points = []
    caption_points = []
    count = 0
    for image_path in dir_path.glob("*.jpg"):
        image_embedding = get_image_embedding(image_path)[0].tolist()
        text_embedding = get_text_embedding(captions[image_path.name])[0].tolist()

        # We assume that the collection is already created with the correct config
        scene_points.append(
            models.PointStruct(
                id=generate_id(image_path.name, movie_id),
                vector=image_embedding,
                payload={
                    "movie_id": movie_id,
                    "director": movie_info[movie_id]["Director"],
                    "actor": movie_info[movie_id]["Actors"],
                    "genre": movie_info[movie_id]["Genre"],
                    "year": movie_info[movie_id]["Year"],
                    "caption": captions[image_path.name],
                    "image_path": f"/images/{movie_id}/{image_path.name}",
                },
            )
        )
        caption_points.append(
            models.PointStruct(
                id=generate_id(image_path.name, movie_id),
                vector=text_embedding,
                payload={
                    "movie_id": movie_id,
                    "director": movie_info[movie_id]["Director"],
                    "actor": movie_info[movie_id]["Actors"],
                    "genre": movie_info[movie_id]["Genre"],
                    "year": movie_info[movie_id]["Year"],
                    "image_path": f"/images/{movie_id}/{image_path.name}",
                },
            )
        )
        count += 1

    client.upload_points("scenes", scene_points)
    client.upload_points("captions", caption_points)
