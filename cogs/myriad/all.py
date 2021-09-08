"""Myriad module."""

from myriad import sailor_cogs


def setup(processor):
    """Set up the cogs."""
    sailor_cogs.setup(processor)


def unload(processor):
    """Tear down the cogs."""
    sailor_cogs.unload(processor)
