import cv2
from deepface import DeepFace
from loguru import logger

from openers.fileopener import FileOpener
from processors.base import BaseProcessor, ProcessorResult
from criteria.trafficking import is_possible_trafficking
from agents.namus import NamusSearchAgent

# TODO
# Make async and then just invoke the deepface calls with to_thread
# or run_in_executor
class DeepFaceProcessor(BaseProcessor):
    """A processor which uses the python deepface module
    to analyze images for human trafficking.

    This processor will process a stream of video frames. It
    will the use python deepface to detect any forms of human
    trafficking and, if found, then perform biometric identification.
    """
    BATCH_SIZE: int = 5  # analyze only every x frames

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_stream(self, stream: str):
        """Process the input stream and, on each frame,
        perform deepdace analysis.
        """
        search_agent = NamusSearchAgent()
        with FileOpener(stream) as o:
            f = o.read_one()
            count = 0
            while f is not None:
                if count % DeepFaceProcessor.BATCH_SIZE == 0:
                    res = self.process_frame(f)

                    if res.is_trafficking:
                        logger.info("Found trafficking victim")
                        # this would be better again going through
                        # rabbitmq to some other service
                        search_agent.search_victims(f, res.victims)

                f = o.read_one()

    def process_frame(self, frame):
        """Process a single frame
        """
        res = DeepFace.analyze(
            frame,
            enforce_detection=False,
            detector_backend=self.detector_backend,
            actions=self.actions,
            silent=True,
        )

        logger.info(res)

        ret = ProcessorResult(is_trafficking=False, victims=[])

        if len(res) > 0 and is_possible_trafficking(res):
            ret.is_trafficking = True
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
