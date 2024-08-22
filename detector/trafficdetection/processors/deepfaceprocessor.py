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
    BATCH_SIZE: int = 1  # analyze only every x frames
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_stream(self, stream: str):
        """Process the input stream and, on each frame,
        perform deepdace analysis.
        """
        search_agent = NamusSearchAgent()
        output = f"{stream}.processed.avi"

        with FileOpener(stream) as o:
            fps = o._cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(o._cap.get(3))
            frame_height = int(o._cap.get(4))
            output_writer = cv2.VideoWriter(output,cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))

            f = o.read_one()
            count = 0
            while f is not None:
                if count % DeepFaceProcessor.BATCH_SIZE == 0:
                    logger.info(f"{stream=}, {count=}")
                    res = self.process_frame(f)
                    output_writer.write(res)

                    # if res.is_trafficking:
                    #    logger.info("Found trafficking victim")
                        # this would be better again going through
                        # rabbitmq to some other service
                        # search_agent.search_victims(f, res.victims)

                f = o.read_one()
                count += 1
            output_writer.release()

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

        # logger.info(res)

        ret = ProcessorResult(is_trafficking=False, victims=[])
        
        curr_y = 5
        curr_x = 0
        (jump_x, jump_y), _ = cv2.getTextSize(
            "Emotion: Disgust", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
        )

        if len(res) > 0 and is_possible_trafficking(res):
            ret.is_trafficking = True
            for idx, r in enumerate(res):
                age = r["age"]
                gender = r["dominant_gender"]
                race = r["dominant_race"]
                emotion = r["dominant_emotion"]
                region = r["region"]
                x, y, w, h = region["x"], region["y"], region["w"], region["h"]

                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)

                labels = [
                    f"Age: {age}",
                    f"Gender: {gender}",
                    f"Race: {race}",
                    f"Emotion: {emotion}",
                ]
                # cv2.rectangle(
                #     frame,
                #     (curr_x, curr_y - jump_y),
                #     (curr_x + jump_x, curr_y + len(labels) * jump_y),
                #     (255, 255, 255),
                #     -1,
                # )

                for label in labels:
                    cv2.putText(
                        frame,
                        label,
                        (curr_x, curr_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (0, 0, 0),
                        1,
                    )
                    curr_y += jump_y
                curr_x += jump_x
                curr_y = 30

                # ret.victims.append(
                #     {
                #         "age": age,
                #         "gender": gender,
                #         "race": race,
                #         "emotion": emotion,
                #     }
                # )
        return frame
