import logging

import aiopg
from psycopg2.extras import DictCursor


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('PG plugin inited')

    """
    Requires body params:
    pg:
      user: (optional - will be taken from config)
      host:
      port: (optional - will be taken from config)
      database:
      query:
      query_params: (optional)
    """
    async def process(self, body):
        logging.info('PG plugin process called')
        # Connect to db
        async with aiopg.create_pool(
            user=self.kwargs['global_config']['db']['user'],
            host=body['host'],
            port=self.kwargs['global_config']['db']['port'],
            database=body['database'],
            password=self.kwargs['global_config']['db']['password'],
            ) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(cursor_factory=DictCursor) as cur:
                    await cur.execute("BEGIN")
                    try:
                        # Make request
                        await cur.execute(body['query'], body.get('query_params', None))
                        # Fetch data
                        records = await cur.fetchall()
                        records = [dict(r) for r in records]
                        cur.execute("COMMIT")
                    except Exception as e:
                        logging.error(e)
                        records = [ {} ]
                        await cur.execute("ROLLBACK")
                    finally:
                        cur.close()

        # Form MD table
        headers = list( records[0].keys() )
        result_formatted = ' | '.join(headers)
        result_formatted = '\n'.join( [
            result_formatted,
            '|'.join( ['-'] * len(headers) )
            ]
        )

        data_array = []
        for r in records:
            data = [
                r[h] for h in headers
            ]
            data_array.append( '|'.join([ str(d) for d in data ]) )

        result_formatted = '\n'.join( [ result_formatted ] + data_array )

        logging.debug('Processing finished')

        return {
                "head": "### <pre>{}/{}: {} | {}</pre>".format(
                    body['host'],
                    body['database'],
                    body['query'],
                    body.get('query_params', None)
                ),
                "body": result_formatted
                }
