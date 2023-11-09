class BaseReader:
    def __init__(
        self,
        detector_backend="retinaface",
        actions=["age", "gender", "race", "emotion"],
    ):
        self.detector_backend = detector_backend
        self.actions = actions

    def read(self):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def process(self, frame, add_labels=True):
        raise NotImplementedError
