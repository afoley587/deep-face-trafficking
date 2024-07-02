from typing import List, Dict, Union, Optional, Any
from pydantic import BaseModel, Field


class BaseProcessor:
    def __init__(
        self,
        detector_backend: str = "retinaface",
        actions: List[str] = ["age", "gender", "race", "emotion"],
    ):
        self.detector_backend = detector_backend
        self.actions = actions

    def process_stream(self, stream: str):
        raise NotImplementedError

    def process_frame(self, frame):
        raise NotImplementedError


class ProcessorResult(BaseModel):
    is_trafficking: bool
    victims: List[Dict[Any, Any]]
