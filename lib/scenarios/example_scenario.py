import logging


class Scenario:
    def __init__(self, *args, **kwargs):
        self.plugins = kwargs['plugins']
        logging.info('ExampleScenario inited')

    def process(self, alert):
        logging.info('ExampleScenario process called')
        ex_plug = self.plugins['example_plugin'].Plugin()
        ex_plug.process(alert)
