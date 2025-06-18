"""
I.N.S.I.G.H.T. Renderer Package

This package contains all rendering components for the I.N.S.I.G.H.T. platform:
- ConsoleRenderer: For terminal/console output
- HTMLRenderer: For HTML dossier generation

All rendering logic is centralized here to keep main.py clean and focused
on core orchestration and debugging logic.
"""

from .console_renderer import ConsoleRenderer
from .html_renderer import HTMLRenderer

__all__ = ['ConsoleRenderer', 'HTMLRenderer'] 