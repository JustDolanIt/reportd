import logging


class Scenario:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.plugins = kwargs['plugins']
        logging.info('ExampleScenario inited')

    async def process(self, alert):
        logging.info('ExampleScenario process called')

        ex_plug = self.plugins['example_plugin'].Plugin(**self.kwargs)
        ex_result.append(await ex_plug.process(alert))
        ex_result_formatted = """
{}

{}
        """.format(ex_result['head'], ex_result['body'])

        return """
## Alert data

{}""".format(
            ex_result_formatted
            )
