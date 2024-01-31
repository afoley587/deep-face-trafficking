import threading
import queue
import cv2
from deepface import DeepFace
from loguru import logger
from .base import BaseReader


class BufferedVideoReader(BaseReader):
    def __init__(self, name, analyze_every=10, **kwargs):
        super().__init__(**kwargs)
        self.cap = cv2.VideoCapture(name)
        self.analyze_every = analyze_every
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        self.count = 0
        self.prev = []
        t.daemon = True
        t.start()

    def set_analyze_every(self, analyze_every):
        self.analyze_every = analyze_every

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            self.q.put(frame)
            self.count += 1

    def read(self):
        try:
            return self.q.get(block=True, timeout=1)
        except queue.Empty:
            return None

    def get(self, prop):
        return self.cap.get(prop)

    def process(self, frame, add_labels=True):
        if self.count % self.analyze_every == 0:
            res = DeepFace.analyze(
                frame,
                enforce_detection=False,
                detector_backend=self.detector_backend,
                actions=self.actions,
                silent=True,
            )

            self.prev = res

        if len(self.prev) > 0:
            curr_y = 30
            curr_x = 0
            (jump_x, jump_y), _ = cv2.getTextSize(
                "Emotion: Disgust", cv2.FONT_HERSHEY_SIMPLEX, 2, 2
            )

            for idx, r in enumerate(self.prev):
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
                    2,
                    (0, 0, 0),
                    2,
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
                            2,
                            (0, 0, 0),
                            2,
                        )
                        curr_y += jump_y
                    curr_x += jump_x
                    curr_y = 30
        return frame, self.prev
