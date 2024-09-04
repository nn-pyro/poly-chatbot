FROM python:3.11-slim

WORKDIR /poly_chatbot_ver3

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip \
    && pip cache purge \
    && pip install --no-cache-dir -r requirements.txt
    
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
