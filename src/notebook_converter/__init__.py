"""
Jupyter Notebook to Interactive Web Application Converter

This package provides tools to convert Jupyter Notebooks into interactive
Streamlit web applications with parameterized inputs and interactive visualizations.
"""

__version__ = "0.1.0"

from .converter import NotebookConverter

__all__ = ["NotebookConverter"]
