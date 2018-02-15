import logging

import aiopg
from psycopg2.extras import DictCursor


class Query:

    __query = """
        SELECT
        id
       ,scenarios
       ,kwargs
       ,name_prefix
       ,description
    FROM reportd.reports
    WHERE (
            status >= %(status)s
        AND (
                %(severity)s && (severity)
            OR
                severity IS NULL
        )
        AND (
               NOT (%(service)s && (exclude_services))
            OR
                exclude_services IS NULL
        )
        AND (
                %(service)s && (services)
            OR
                services IS NULL
        )
        AND (
               NOT (%(resource)s && (exclude_resource))
            OR
                exclude_resource IS NULL
        )
        AND (
                %(tags)s && (tags)
            OR
                tags IS NULL
        )
        AND (
               NOT (%(tags)s && (exclude_tags))
            OR
                exclude_tags IS NULL
        )
        AND (
                %(event)s && (events)
            OR
                events IS NULL
        )
        AND (
               NOT (%(event)s && (exclude_events))
            OR
                exclude_events IS NULL
        )
    )
    """

    def __init__(self, conf):
        self.conf = conf
        self.conn = None

    async def connect(self):
        if self.conn is None:
            pool = await aiopg.create_pool(
                host=self.conf['db']['host'],
                port=self.conf['db']['port'],
                database=self.conf['db']['database'],
                user=self.conf['db']['user'],
                password=self.conf['db']['password'],
            )
            self.conn = await pool.acquire()
            logging.debug("Connect to database: %r" % self.conf['db']['database'])

    def preconfig(self, body):
        body['severity'] = [ body['severity'] ]
        body['resource'] = [ body['resource'] ]
        body['event'] = [ body['event'] ]
        return body

    async def stop(self):
        if self.conn is not None:
            if not self.conn.closed:
                await self.conn.close()

    async def get_scenarios(self, params):

        query = Query.__query

        cursor = await self.conn.cursor(cursor_factory=DictCursor)
        await cursor.execute("BEGIN")

        try: 
            await cursor.execute(query, self.preconfig(params))
            records = await cursor.fetchall()
        except Exception as e:
            logging.error(e)
            await cursor.execute("ROLLBACK")
            records = []
        finally:
            cursor.close()

        return [dict(r) for r in records]
