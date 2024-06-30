# import os
# import utils
# from loguru import logger
# from criteria.trafficking import is_possible_trafficking

# import asyncio
import signal
import sys
import os

from readers.asyncpikareader import ReconnectingAsyncPikaReader


def start():
    amqp_url = "amqp://guest:guest@rabbitmq:5672/%2F"
    consumer = ReconnectingAsyncPikaReader(amqp_url)
    consumer.stream()


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        try:
            sys.exit(signal.SIGINT)
        except SystemExit:
            os._exit(signal.SIGINT)