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
        try:
            async with asyncssh.connect(
                    body['host'],
                    known_hosts=None,
                    username=body.get(
                        'user',
                        self.kwargs['global_config']['ssh']['user'] )
                    ) as conn:
                res = await conn.run(
                        body['commands'],
                        check=False
                        )
                result = res.stdout
        except Exception as e:
            logging.error(e)
            result = 'Execution error'

        return "\n".join( (
            'Commands:', body['commands'], '---', 'Output:', result
        ) )
