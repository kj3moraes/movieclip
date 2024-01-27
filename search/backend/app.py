from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from qdrant_client import models, QdrantClient
from image_ingestion import *
from image_search import *

app = FastAPI()
# Mount a static directory to serve images from
app.mount("/images", StaticFiles(directory="../image_data"), name="images")

client = QdrantClient("localhost", port=6333)


class SearchRequest(BaseModel):
    text: str
    k: Optional[int] = None


# Ingest endpoint
@app.get("/api/ingest", status_code=201)
async def ingest():
    # recreate_collection will delete the collection if it already exists
    client.recreate_collection(
        collection_name="scenes",
        vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
    )
    client.recreate_collection(
        collection_name="captions",
        vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
    )

    try:
        # Iterate through each of the directories and upsert them
        # into the Qdrant db
        for dir_path in Path("../image_data").iterdir():
            if dir_path.is_dir():
                ingest_dir(dir_path, client)
    except:
        return {"message": "Ingest failed"}
    return {"message": "Ingest successful"}


# Search endpoint
@app.post("/api/search")
async def search(request: SearchRequest):
    # We assume that the collection is already created with the correct config
    if request.k is None:
        request.k = 10
    try:
        results = search_text(request.text, request.k, client)
        return {"message": "Search successful", "results": results}
    except:
        return {"message": "Search failed"}


# Run the server using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
