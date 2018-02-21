import logging
import json
import base64
import datetime

import aiohttp


"""
https://aminux.wordpress.com/2017/05/04/grafana-export-png-external-system/

example:
curl -H "Authorization: GRAFANA_USER GRAFANA_APIKEY" -k 'https://grafana.app.ipl/render/d-solo/000000038/bc?refresh=1m&panelId=20&orgId=1&width=1000&height=500&tz=UTC%2B03%3A00&from=1519212235237&to=1519223035237'

base:
https://grafana.app.ipl/d/000000038/bc?refresh=1m&panelId=20&fullscreen&orgId=1&from=1519212235237&to=1519223035237
"""
class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('Grafana plugin inited')

    """
    Requires body params:
    http:
      url: 
      ssl_verify: (optional - False)
      offset_secs: (optional - will be used default in dashboard)
    """
    async def process(self, body):
        logging.info('Grafana plugin process called')

        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    verify_ssl=body.get('ssl_verify', False)
                    )
                ) as session:
            if 'offset_secs' in body:
                from_param = datetime.datetime.now() - datetime.timedelta(seconds=body['offset_secs'])
                body['url'] = body['url'] + '&from={}'.format(
                        int(from_param.timestamp() * 1000)
                    )
            async with session.get(
                    body['url'],
                    headers={
                        "Authorization": "{} {}".format(
                            self.kwargs['global_config']['grafana']['user'],
                            self.kwargs['global_config']['grafana']['apikey']
                            )
                        }
                    ) as resp:
                screen = await resp.read()
                screen_encoded = base64.encodestring(screen).decode()

        logging.debug('Processing finished')

        return {
                "head": "### {}".format(body['url']),
                "body": '<img src="data:image/png;base64, {}" alt="Grafana graph" />'.format(screen_encoded)
                }
