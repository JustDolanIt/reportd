import logging
import os
import importlib


MainModule = "__init__"
PluginsFolder = "./lib/plugins"
ScenariosFolder = "./lib/scenarios"


class Reporter():
    def __init__(self, *args, **kwargs):
        self.plugins = self.get_plugins()
        self.scenarios = self.get_scenarios()

    def get_plugins(self):
        plugins = {}
        possible_plugins = os.listdir(PluginsFolder)
        for plugin_file in possible_plugins:
            plugin_name = plugin_file.split('.py')[0]
            if plugin_name != MainModule and plugin_name[0] != '.' and not os.path.isdir('/'.join( (PluginsFolder, plugin_name) ) ):
                plugin = importlib.import_module('lib.plugins.{}'.format(
                        plugin_name
                    ))
                plugins.update({plugin_name: plugin})
        return plugins

    def get_scenarios(self):
        scenarios = {}
        possible_scenarios = os.listdir(ScenariosFolder)
        for scenario_file in possible_scenarios:
            scenario_name = scenario_file.split('.py')[0]
            if scenario_name != MainModule and scenario_name[0] != '.' and not os.path.isdir('/'.join( (ScenariosFolder, scenario_name) ) ):
                scenario = importlib.import_module('lib.scenarios.{}'.format(
                        scenario_name
                    ))
                scenarios.update({scenario_name: scenario})
        return scenarios
