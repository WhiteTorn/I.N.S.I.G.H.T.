"""
I.N.S.I.G.H.T. Output Package

This package contains all output format handlers for the I.N.S.I.G.H.T. platform:
- ConsoleOutput: For terminal/console output
- HTMLOutput: For HTML dossier generation  
- JSONOutput: For JSON file export

All output logic is centralized here to keep main.py clean and focused
on core orchestration and debugging logic.

Output formats are designed to be easily integrable in main.py through
a unified interface pattern.
"""

from .console_output import ConsoleOutput
from .html_output import HTMLOutput
from .json_output import JSONOutput

__all__ = ['ConsoleOutput', 'HTMLOutput', 'JSONOutput'] 