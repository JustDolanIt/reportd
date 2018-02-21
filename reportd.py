#!/usr/bin/env python3
import argparse
import asyncio
import functools
import os
import signal
import logging
import datetime

import aioamqp
import yaml
import markdown

from lib import Reporter
from lib.query import Query


# Globals
REPORTER = None
QUERY = None
CONFIG = None


def ask_exit(signame):
    logging.info("Got signal %s: exit" % signame)
    loop.stop()

def parse_config(filepath=None):
    try:
        with open(filepath) as f:
            config = yaml.safe_load(f.read())
        return config
    except Exception as e:
        logging.error("config parsing error")
        logging.error(e)
        return None


async def callback(channel, body, envelope, properties):
    # Get scenario mapping from database for body
    body_dict = yaml.safe_load(body.decode())
    logging.info(body_dict)
    scenarios_todo = await QUERY.get_scenarios(body_dict)
    logging.debug(scenarios_todo)

    plugins = REPORTER.get_plugins()
    logging.debug(plugins)

    scenarios = REPORTER.get_scenarios()
    logging.debug(scenarios)

    for scen_global in scenarios_todo:
        scen_results = {}
        for scen_local in scen_global['scenarios']:
            used_kwargs = scen_global['kwargs'] or {}
            # Passing config as kwargs key for some plugins (Data sources)
            used_kwargs.update({"global_config": CONFIG})
            scen = scenarios[scen_local].Scenario(plugins=plugins, **used_kwargs)
            scen_results.update({
                scen_local: await scen.process(body)
                })
        # form report and save
        if not os.path.exists(CONFIG['reports_dir']):
            os.makedirs(CONFIG['reports_dir'])
        with open("{}/{}_{}_{}.html".format(
                CONFIG['reports_dir'],
                scen_global['name_prefix'],
                body_dict['id'],
                datetime.datetime.now().isoformat()
        ), 'w') as out_f:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.toc',
                'markdown.extensions.tables',
                'markdown.extensions.sane_lists',
                'markdown.extensions.smarty',
                'markdown.extensions.extra'
            ])
            scen_results_md = ["""
# {}

{}

            """.format(k, v) for k, v in  scen_results.items()]
            html = md.convert('\n'.join(['[TOC]', '\n'] + scen_results_md ))
            pre_html = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style>
table {
  border-collapse: collapse; border: 1px solid black;
}
td,th {
  border-collapse: collapse; border: 1px solid black; padding: 0.5em;
}
</style>
</head>
"""
            html = """
<body>
{}
</body>
</html>
            """.format(
                html
                    )
            out_f.write(pre_html+html)

        logging.info("Processing finished")

    await channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag,
    )

async def connect():
    try:
        transport, protocol = await aioamqp.connect(
            **CONFIG['alerta']['amqp']
        )
    except aioamqp.AmqpClosedConnection:
        logging.info("closed connections")
        return

    await QUERY.connect()

    channel = await protocol.channel()

    await channel.queue_declare(
            queue_name=CONFIG['alerta']['queue'],
            durable=True
        )
    await channel.basic_consume(
            callback,
            queue_name=CONFIG['alerta']['queue']
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config/config.yaml')
    args = parser.parse_args()
    args_vars = vars(args)
    CONFIG = parse_config(args_vars['config'])

    # Logging
    numeric_level = getattr(
            logging,
            CONFIG['log_level'].upper(),
            None
            )
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(
            level=numeric_level,
            format='{"stamp": "%(asctime)s", "level": "%(levelname)s", "func": "%(funcName)s", "module": "%(module)s",  "message": "%(message)s"}'
            )
    logging.info("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())

    # Reporter class
    REPORTER = Reporter()
    # Query class
    QUERY = Query(CONFIG)

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    loop.run_until_complete(
        connect()
    )
    loop.run_forever()
