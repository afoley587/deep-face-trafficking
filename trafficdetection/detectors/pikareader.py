import cv2
from deepface import DeepFace
from .base import BaseReader
import pika
from pika.exchange_type import ExchangeType

class PikaReader(BaseReader):
    EXCHANGE = "videostreams"
    BIND_KEY = "streams"

    def __init__(self, host, virtual_host, username, password, **kwargs):
        super().__init__(**kwargs)
        self._params = pika.connection.ConnectionParameters(
            host=host,
            virtual_host=virtual_host,
            credentials=pika.credentials.PlainCredentials(username, password),
        )
        self._conn = None
        self._channel = None
        self._queue = None
        self.connect() # fix this

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.exchange_declare(exchange=self.EXCHANGE, type=ExchangeType.topic, durable=True)
            self._queue = self._channel.queue_declare(queue='', exclusive=True)
            self._channel.queue_bind(queue=self._queue.queue.name, exchange=self.EXCHANGE, routing_key=self.BIND_KEY)
            self._channel.basic_consume(self._queue.queue.name, on_message_callback=self.read, auto_ack=True)

    def read(self, ch, method, properties, body):
        # TODO read from stream
        # and then invoke process callback
        print(ch, method, properties, body)

    def get(self, prop):
        return None

    def process(self, frame, add_labels=True):
        res = DeepFace.analyze(
            frame,
            enforce_detection=False,
            detector_backend=self.detector_backend,
            actions=self.actions,
            silent=True,
        )

        curr_y = 30
        curr_x = 0
        (jump_x, jump_y), _ = cv2.getTextSize(
            "Emotion: Disgust", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
        )

        for idx, r in enumerate(res):
            age = r["age"]
            gender = r["dominant_gender"]
            race = r["dominant_race"]
            emotion = r["dominant_emotion"]
            region = r["region"]
            x, y, w, h = region["x"], region["y"], region["w"], region["h"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
            cv2.putText(
                frame,
                f"ID: {idx}",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                1,
            )

            if add_labels:
                labels = [
                    f"ID: {idx}",
                    f"Age: {age}",
                    f"Gender: {gender}",
                    f"Race: {race}",
                    f"Emotion: {emotion}",
                ]
                cv2.rectangle(
                    frame,
                    (curr_x, curr_y - jump_y),
                    (curr_x + jump_x, curr_y + len(labels) * jump_y),
                    (255, 255, 255),
                    -1,
                )

                for label in labels:
                    cv2.putText(
                        frame,
                        label,
                        (curr_x, curr_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 0),
                        1,
                    )
                    curr_y += jump_y
                curr_x += jump_x
                curr_y = 30
        return frame, res
