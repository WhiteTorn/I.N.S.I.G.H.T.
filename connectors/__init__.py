"""
I.N.S.I.G.H.T. Mark II - Connector Package
The modular connector architecture for multi-source intelligence gathering.
"""

from .base_connector import BaseConnector
from .telegram_connector import TelegramConnector

__all__ = ['BaseConnector', 'TelegramConnector'] 