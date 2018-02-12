import logging


class Plugin:
    def __init__(self, *args, **kwargs):
        logging.info('ExamplePlugin inited')

    def process(self, alert):
        logging.info('ExamplePlugin process called')
        logging.info(alert)
