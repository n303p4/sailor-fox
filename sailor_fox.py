"""Subclass sailor Processor."""

import json

import sailor


class ProcessorWithConfig(sailor.commands.Processor):
    """Subclass of Processor with configuration."""

    def __init__(self, *args, **kwargs):
        super(ProcessorWithConfig, self).__init__(*args, **kwargs)
        self.description = "This is a bot."
        self.config = {}

    def load_config(self, filename: str = "config.json"):
        """Load configuration."""
        with open(filename, "r") as file_object:
            self.config = json.load(file_object)

        self.name = self.config.get("name", self.name)
        self.description = self.config.get("description", self.description)

    def save_config(self, filename: str = "config.json"):
        """Save configuration."""
        with open(filename, "w") as file_object:
            json.dump(self.config, file_object, indent=4)
