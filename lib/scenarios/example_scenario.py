import logging


class Scenario:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.plugins = kwargs['plugins']
        logging.info('ExampleScenario inited')

    def process(self, alert):
        logging.info('ExampleScenario process called')
        ex_plug = self.plugins['example_plugin'].Plugin(**self.kwargs)
        plugin_results = []

        plugin_results.append(ex_plug.process(alert))

        return "\n!!!!!!!!\n".join(plugin_results)
