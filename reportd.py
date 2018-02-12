import argparse
import asyncio
import functools
import os
import signal
import logging

import aioamqp
import yaml

from lib import Reporter


# Globals
REPORTER = None


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
    logging.info(yaml.safe_load(body.decode()))

    # Get scenario mapping from database for body
    print(REPORTER)

    plugins = REPORTER.get_plugins()
    print(plugins)

    scenarios = REPORTER.get_scenarios()
    print(scenarios)
    example_scanario = scenarios['example_scenario'].Scenario(plugins=plugins)
    example_scanario.process(body)

    await channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag,
    )

async def connect(config):
    try:
        transport, protocol = await aioamqp.connect(
            **config['alerta']['amqp']
        )
    except aioamqp.AmqpClosedConnection:
        logging.info("closed connections")
        return

    channel = await protocol.channel()

    await channel.queue_declare(
            queue_name=config['alerta']['queue'],
            durable=True
        )
    await channel.basic_consume(
            callback,
            queue_name=config['alerta']['queue']
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config/config.yaml')
    args = parser.parse_args()
    args_vars = vars(args)
    config = parse_config(args_vars['config'])

    # Logging
    numeric_level = getattr(
            logging,
            config['ops']['log_level'].upper(),
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

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    loop.run_until_complete(
        connect(config)
    )
    loop.run_forever()
