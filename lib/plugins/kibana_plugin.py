import logging
import datetime


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.ws_plgn = self.kwargs['plugins']['web_screenshot_plugin'].Plugin(*args, **kwargs)
        logging.info('Kibana plugin inited')

    """
    Requires body params:
    kibana:
        columns: (optional - will use ['_source'])
        time_from: (optinal - will use 'now-15m')
        time_to: (optinal - will use 'now')
        query: (optinal - will use '')
        sort_field: (optinal - will use '@timestamp')
        sort_method: (optional - will user desc)
    """
    async def process(self, body):
        logging.info('Kibana plugin process called')

        ws_body = {
                'page': "{}/app/kibana#/discover?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'{}',mode:absolute,to:'{}'))&_a=(columns:!({}),interval:auto,query:(language:lucene,query:'{}'),sort:!('{}',{}))".format(
                    self.kwargs['global_config']['kibana']['url_base'],
                    body.get('time_from', 'now-15m'),
                    body.get('time_to', 'now'),
                    ','.join(body.get('columns', ['_source'])),
                    body.get('query', ''),
                    body.get('sort_field', '@timestamp'),
                    body.get('sort_method', 'desc')
                ),
                'xpath': '/html/body/div[1]/div/div/div[3]/discover-app/main/div[2]/div[2]/div/div[2]/section[1]/visualization/div/div/div/div[2]/div[2]/div',
                'wait': self.kwargs['global_config']['kibana']['wait'],
                'width': self.kwargs['global_config']['kibana']['width'],
                'height': self.kwargs['global_config']['kibana']['height']
                }

        res = await self.ws_plgn.process(ws_body)

        logging.debug('Processing finished')

        return {
                "head": res['head'],
                "body": res['body']
                }
