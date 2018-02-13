import logging


class Scenario:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.plugins = kwargs['plugins']
        logging.info('ExampleScenario inited')

    async def process(self, alert):
        logging.info('ExampleScenario process called')
        plugin_results = []

        ex_plug = self.plugins['example_plugin'].Plugin(**self.kwargs)
        plugin_results.append(await ex_plug.process(alert))

        return "\n!!!!!!!!\n".join(plugin_results)
