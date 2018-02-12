import logging


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('ExamplePlugin inited')

    def process(self, alert):
        logging.info('ExamplePlugin process called')
        logging.info(alert)

        return "\n".join( (
            alert.decode(), '---', 'processed'
        ) )
