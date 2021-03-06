import logging
import json


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('Example plugin inited')

    async def process(self, body):
        logging.info('Example plugin process called')

        logging.debug('Processing finished')

        return {
                "head": "### Message body",
                "body": "<pre>\n{}\n</pre>".format(json.dumps(
                        json.loads(body.decode()),
                        indent=2,
                        sort_keys=True
                        )
                    )
                }
