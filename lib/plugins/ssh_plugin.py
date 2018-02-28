import logging

import asyncssh


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('SSH plugin inited')

    """
    Requires body params:
    ssh:
      user: (optional - will be taken from config)
      host:
      commands: (example - "hostname && date && sudo systemctl status zabbix-agent")
    """
    async def process(self, body):
        logging.info('SSH plugin process called')
        username=body.get(
            'user',
            self.kwargs['global_config']['ssh']['user'] )
        try:
            async with asyncssh.connect(
                    body['host'],
                    known_hosts=None,
                    username=username,
                    client_keys=[self.kwargs['global_config']['ssh']['id_rsa_filepath']]
                    ) as conn:
                res = await conn.run(
                        body['commands'],
                        check=False
                        )
                result = res.stdout
        except Exception as e:
            logging.error(e)
            result = 'Execution error'

        logging.debug('Processing finished')

        return {
                "head": '### <code>{}@{} $ {}</code>'.format(username, body['host'], body['commands']),
                "body": '<pre>\n{}\n</pre>'.format(result)
                }
