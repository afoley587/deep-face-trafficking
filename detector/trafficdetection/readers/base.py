class BaseStreamer:
    """Defines an interface for a basic streamer.

    A streamer object consists of a stream method
    which listens on some sort of input stream (ie rabbitmq)
    and acts on it. Could also be a consumer method, but streamer
    is more generic as this could be a file or something similar.
    """
    def stream(self):
        raise NotImplementedError
