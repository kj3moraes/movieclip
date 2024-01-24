# Moviesearch

Using the fine-tuned model trained before, we can now generate custom image embeddings for a custom set of images. This is an app to run this demo for custom images.

## Setup

To run this app locally, you need to have the frontend, backend and vector store dependencies installed.

### Frontend Dependencies

Install the frontend dependencies with

```bash
npm run dev
```

(or whatever package manager you use)

### Backend Dependencies

Install the backend dependencies with poetry on Python3.11 using

```bash
poetry shell
```

If you don't have poetry, (start a virtual environment and) install all the packages from the requirements.txt file

```bash
pip install -r requirements.txt
```

### Vector Store

You need to have Qdrant running for this app to work. Install it with

```bash
docker pull qdrant/qdrant
```

Furthermore, you can add whatever custom images that you want in the `image_data/` directories. Only `*.jpg` are read.

## Running

To run this app, you need to start the

1. Qdrant Vector Store

```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z -e QDRANT__SERVICE__GRPC_PORT="6334" qdrant/qdrant```
```

2. Backend Server

```bash
cd backend/
uvicorn server:app --reload
```

3. Frontend

```bash
npm run dev
```

The application will start runnign at `localhost:3000`


