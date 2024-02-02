import cv2
from deepface import DeepFace
from loguru import logger

from readers.openers.fileopener import FileOpener
from readers.processors.base import BaseProcessor

class DeepFaceProcessor(BaseProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_stream(self, file):
        with FileOpener(file) as o:
            f = o.read_one()
            while f is not None:
                self.process_frame(f)
                f = o.read_one()

    def process_frame(self, frame, add_labels=True):
        logger.info("Processing frame....")
        res = DeepFace.analyze(
            frame,
            enforce_detection=False,
            detector_backend=self.detector_backend,
            actions=self.actions,
            silent=True,
        )

        if len(res) > 0:
            curr_y = 30
            curr_x = 0
            (jump_x, jump_y), _ = cv2.getTextSize(
                "Emotion: Disgust", cv2.FONT_HERSHEY_SIMPLEX, 2, 2
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
        return frame, res