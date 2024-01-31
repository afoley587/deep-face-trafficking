import json
import pika
from loguru import logger


class BasePublisher:
    EXCHANGE = "BASE"
    TYPE = "BASE"
    ROUTING_KEY = "BASE"

    def __init__(self, host, virtual_host, username, password):
        self._params = pika.connection.ConnectionParameters(
            host=host,
            virtual_host=virtual_host,
            credentials=pika.credentials.PlainCredentials(username, password),
        )
        self._conn = None
        self._channel = None

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.exchange_declare(exchange=self.EXCHANGE, type=self.TYPE)

    def _publish(self, msg):
        self._channel.basic_publish(
            exchange=self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            body=json.dumps(msg).encode(),
        )
        logger.debug("message sent: %s", msg)

    def publish(self, msg):
        """Publish msg, reconnecting if necessary."""

        try:
            self._publish(msg)
        except pika.exceptions.ConnectionClosed:
            logger.debug("reconnecting to queue")
            self.connect()
            self._publish(msg)

    def close(self):
        if self._conn and self._conn.is_open:
            logger.debug("closing queue connection")
            self._conn.close()


class ImagePublisher(BasePublisher):
    EXCHANGE = "incoming_images"
    TYPE = "topic"
    ROUTING_KEY = "BASE"

    def __init__(self, routing_key, **kwargs):
        super().__init__(**kwargs)
        self.ROUTING_KEY = routing_key
