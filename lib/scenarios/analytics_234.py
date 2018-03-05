import logging

class Scenario:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.plugins = kwargs['plugins']
        logging.info('Test scenario inited')

    async def process(self, alert):
        logging.info('ANALYTICS-234 process called')

        pg = []
        pg_plug = self.plugins['pg_plugin'].Plugin(**self.kwargs)
        for pg_data in self.kwargs['pg']:
            pg.append(await pg_plug.process(pg_data))

        pg_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in pg])

        return """
## PostgreSQL

{}

{}
        """.format(
            pg_formatted,
            )
