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
    director: Optional[str] = None
    actor: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[str] = None


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
        with open("../image_data/results.json") as f:
            results = json.load(f)
        # Iterate through each of the directories and upsert them
        # into the Qdrant db
        for dir_path in Path("../image_data").iterdir():
            if dir_path.is_dir():
                ingest_dir(dir_path, client, results)
    except:
        return {"message": "Ingest failed"}
    return {"message": "Ingest successful"}


# Search endpoint
@app.post("/api/search")
async def search(request: SearchRequest):
    # We assume that the collection is already created with the correct config
    request_dict = request.model_dump()
    print("Search request: ", request_dict)
    try:
        text = request_dict.pop("text")
        results = search_text(text, client, **request_dict)
        return {"message": "Search successful", "results": results}
    except:
        return {"message": "Search failed"}


@app.get("/api/delete")
async def delete():
    client.delete_collection("scenes")
    client.delete_collection("captions")
    return {"message": "Delete successful"}

# Run the server using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
