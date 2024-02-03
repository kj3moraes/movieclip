FROM anibali/pytorch:2.0.1-cuda11.8-ubuntu22.04

# Install build-essential for C/C++ compilation
RUN apt update && apt install -y build-essential

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000 
CMD ["uvicorn", "fastapi:app"]