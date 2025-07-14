"""
KiCad Via Grid Generator Plugin
Copyright (c) 2024 Johannes
Licensed under MIT License
"""

from .via_grid_action import ViaGridGeneratorAction

# Register the action plugin
plugin = ViaGridGeneratorAction()
plugin.register()