import logging
import json

import aiohttp


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('HTTP plugin inited')

    """
    Requires body params:
    http:
      url: 
      method: (optional - will use GET)
      body: (optional - will send empty body)
      headers: (optional - will send without headers)
      ssl_verify: (optional - True)
    """
    async def process(self, body):
        logging.info('HTTP plugin process called')

        method = body.get('method', 'get').upper()

        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    verify_ssl=body.get('ssl_verify', None)
                    )
                ) as session:
            methods_map = {
                "GET":     session.get,
                "POST":    session.post,
                "PUT":     session.put,
                "DELETE":  session.delete,
                "HEAD":    session.head,
                "OPTIONS": session.options,
                "PATCH":   session.patch
                }
            async with methods_map[method](
                    body['url'],
                    data=body.get('body', None),
                    headers=body.get('headers', None)
                    ) as resp:

                response_formatted = """
Response code: {}
Response headers:
<pre>
{}
</pre>

Redirection history:
<pre>
{}
</pre>

Response body:

```html
{}
```
                """.format(
                    resp.status,
                    json.dumps(
                        dict(resp.headers),
                        indent=2,
                        sort_keys=True
                    ),
                    resp.history,
                    await resp.text(),
                    )

                logging.debug('Processing finished')

                return {
                        "head": "### HTTP {}: {}".format(
                            method,
                            body['url']
                            ),
                        "body": response_formatted
                    }
