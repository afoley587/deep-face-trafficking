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
    libxext6 \
    libhdf5-dev \
    && mkdir -p /root/.deepface/weights/

ADD https://github.com/serengil/deepface_models/releases/download/v1.0/facial_expression_model_weights.h5 /root/.deepface/weights/facial_expression_model_weights.h5
ADD https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5 /root/.deepface/weights/age_model_weights.h5
ADD https://github.com/serengil/deepface_models/releases/download/v1.0/gender_model_weights.h5 /root/.deepface/weights/gender_model_weights.h5
ADD https://github.com/serengil/deepface_models/releases/download/v1.0/race_model_single_batch.h5 /root/.deepface/weights/race_model_single_batch.h5
ADD https://github.com/serengil/deepface_models/releases/download/v1.0/retinaface.h5 /root/.deepface/weights/retinaface.h5

RUN pip install poetry==1.2.2 \
    && poetry export -f requirements.txt -o requirements.txt --without-hashes \
    && pip install -r requirements.txt \
    && rm -rf requirements.txt \
    && pip uninstall -y poetry

COPY ./trafficdetection /app

CMD ["python3", "/app/main.py", "--rabbit", "foo"]