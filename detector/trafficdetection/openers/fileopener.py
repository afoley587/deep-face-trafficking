import queue
import cv2
from openers.base import BaseOpener


class FileOpener(BaseOpener):
    def __init__(self, path: str = ""):
        super().__init__(path=path)
        self._cap = None

    def read_one(self):
        if not self._cap:
            return None
        if self._cap.isOpened():
            ret, frame = self._cap.read()
            if ret:
                return frame
        return None

    def __enter__(self):
        self._cap = cv2.VideoCapture(self.path)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self._cap.isOpened():
            self._cap.release()
        return self
