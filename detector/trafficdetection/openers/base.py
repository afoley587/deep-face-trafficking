class BaseOpener:
    def __init__(self, path: str = ""):
        self.path = path

    def read_one(self):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, tb):
        raise NotImplementedError
