FROM python:3.11-slim

# Install build-essential for C/C++ compilation
RUN apt update && apt install -y build-essential

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000

# Install the models before the app
CMD ["python", "utils.py"]

CMD ["uvicorn", "app:app"]