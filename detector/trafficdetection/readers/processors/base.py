from typing import List, Dict, Union, Optional
from pydantic import BaseModel, Field
from typing import Any

class BaseProcessor:
    def __init__(
        self,
        detector_backend="retinaface",
        actions=["age", "gender", "race", "emotion"],
    ):
        self.detector_backend = detector_backend
        self.actions = actions

    def process_stream(self, stream):
        raise NotImplementedError

    def process_frame(self, frame, add_labels=True):
        raise NotImplementedError


class ProcessorResult(BaseModel):
    frame: Any
    is_trafficking: bool