# yijing/config/__init__.py

"""
Config Package
=============
Configuration management for the I Ching oracle system.

This package provides:
- Global settings management
- Configuration loading and validation
- Prompt template management
"""

from .settings import Settings, settings

from .settings import Settings, settings, ModelType

__all__ = ['Settings', 'settings', 'ModelType']