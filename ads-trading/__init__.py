"""ADS Trading Package"""
__version__ = "1.0.0"
__author__ = "ADS Trading Team"

from .main import main
from .web_ui.server import WebServer

__all__ = ['main', 'WebServer']