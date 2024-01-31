FROM docker.io/python:3.9.2

RUN mkdir /app
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN apt-get -y update \
    && apt-get install -y \
    python-all-dev \
    libexiv2-dev \
    libboost-python-dev \
    ffmpeg \
    libsm6 \
    libxext6 

RUN pip install poetry==1.2.2 \
    && poetry export -f requirements.txt -o requirements.txt --without-hashes \
    && pip install -r requirements.txt \
    && rm -rf requirements.txt \
    && pip uninstall -y poetry

COPY ./trafficdetection /app

CMD ["python3", "/app/main.py", "--rabbit", "foo"]