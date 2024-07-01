import cv2
from deepface import DeepFace
from loguru import logger

from openers.fileopener import FileOpener
from processors.base import BaseProcessor, ProcessorResult
from criteria.trafficking import is_possible_trafficking
from agents.namus import NamusSearchAgent


class DeepFaceProcessor(BaseProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_stream(self, stream):
        search_agent = NamusSearchAgent()
        with FileOpener(stream) as o:
            f = o.read_one()
            while f is not None:
                res = self.process_frame(f)

                if res.is_trafficking:
                    logger.info("Found trafficking victim")
                    # this would be better again going through
                    # rabbitmq to some other service
                    for v in res.victims:
                        search_agent.search(f, **v)

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

        ret = ProcessorResult(is_trafficking=False, victims=[])
        logger.info(res)

        if len(res) > 0 and is_possible_trafficking(res):
            ret.is_trafficking = True
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

                ret.victims.append(
                    {
                        "age": age,
                        "gender": gender,
                        "race": race,
                        "emotion": emotion,
                    }
                )
        return ret
