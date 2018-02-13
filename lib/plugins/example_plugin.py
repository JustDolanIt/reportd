import logging


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('ExamplePlugin inited')

    async def process(self, body):
        logging.info('ExamplePlugin process called')
        logging.info(body)

        return "\n".join( (
            'Body:', body.decode(), '---', 'Output:', 'processed'
        ) )
