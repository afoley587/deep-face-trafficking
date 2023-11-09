import cv2
from deepface import DeepFace
from .base import BaseReader


class ImageReader(BaseReader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def read(self, filepath):
        return cv2.imread(filepath)

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
