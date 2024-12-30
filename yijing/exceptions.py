# yijing/exceptions.py

"""
Custom Exception Classes for YiJing Package
=========================================

This module defines the exception hierarchy for the YiJing package. Each exception
type corresponds to a specific category of errors that can occur during the
operation of the package.

Exception Hierarchy:
- YijingError (Base)
  ├── ResourceError
  │   ├── ResourceNotFoundError
  │   └── ResourceValidationError
  ├── ModelError
  │   ├── ModelConnectionError
  │   └── ModelResponseError
  ├── HexagramError
  │   ├── InvalidHexagramError
  │   └── HexagramTransformationError
  └── ConfigurationError
      ├── EnvironmentError
      └── SettingsValidationError
"""

class YijingError(Exception):
    """Base exception class for all YiJing-related errors.
    
    This class serves as the parent for all custom exceptions in the package.
    It provides a consistent interface for error handling and allows for
    catching all YiJing-specific errors with a single except clause.
    """
    def __init__(self, message: str = None, *args, **kwargs):
        self.message = message or "Ein unerwarteter Fehler ist aufgetreten"
        super().__init__(self.message, *args)

class ResourceError(YijingError):
    """Base class for errors related to resource handling."""
    def __init__(self, message: str = None, *args, **kwargs):
        super().__init__(message or "Ressourcenfehler aufgetreten", *args)

class ResourceNotFoundError(ResourceError):
    """Raised when a required resource file cannot be found."""
    def __init__(self, resource_path: str, *args, **kwargs):
        message = f"Ressource nicht gefunden: {resource_path}"
        super().__init__(message, *args)
        self.resource_path = resource_path

class ResourceValidationError(ResourceError):
    """Raised when a resource fails validation checks."""
    def __init__(self, resource_path: str, validation_errors: list, *args, **kwargs):
        message = f"Validierungsfehler in Ressource {resource_path}: {', '.join(validation_errors)}"
        super().__init__(message, *args)
        self.resource_path = resource_path
        self.validation_errors = validation_errors

class ModelError(YijingError):
    """Base class for AI model-related errors."""
    def __init__(self, message: str = None, *args, **kwargs):
        super().__init__(message or "KI-Modellfehler aufgetreten", *args)

class ModelConnectionError(ModelError):
    """Raised when connection to the AI model fails."""
    def __init__(self, model_name: str, details: str = None, *args, **kwargs):
        message = f"Verbindung zum Modell {model_name} fehlgeschlagen"
        if details:
            message += f": {details}"
        super().__init__(message, *args)
        self.model_name = model_name
        self.details = details

class ModelResponseError(ModelError):
    """Raised when the AI model returns an invalid or unexpected response."""
    def __init__(self, model_name: str, response: str = None, *args, **kwargs):
        message = f"Ungültige Antwort von Modell {model_name}"
        if response:
            message += f": {response}"
        super().__init__(message, *args)
        self.model_name = model_name
        self.response = response

class HexagramError(YijingError):
    """Base class for hexagram-related errors."""
    def __init__(self, message: str = None, *args, **kwargs):
        super().__init__(message or "Hexagramm-Fehler aufgetreten", *args)

class InvalidHexagramError(HexagramError):
    """Raised when hexagram data is invalid."""
    def __init__(self, hexagram_number: int = None, reason: str = None, *args, **kwargs):
        message = "Ungültiges Hexagramm"
        if hexagram_number is not None:
            message += f" (Nummer {hexagram_number})"
        if reason:
            message += f": {reason}"
        super().__init__(message, *args)
        self.hexagram_number = hexagram_number
        self.reason = reason

class HexagramTransformationError(HexagramError):
    """Raised when there is an error during hexagram transformation."""
    def __init__(self, source_hexagram: int = None, error_detail: str = None, *args, **kwargs):
        message = "Fehler bei der Hexagramm-Transformation"
        if source_hexagram is not None:
            message += f" von Hexagramm {source_hexagram}"
        if error_detail:
            message += f": {error_detail}"
        super().__init__(message, *args)
        self.source_hexagram = source_hexagram
        self.error_detail = error_detail

class ConfigurationError(YijingError):
    """Base class for configuration-related errors."""
    def __init__(self, message: str = None, *args, **kwargs):
        super().__init__(message or "Konfigurationsfehler aufgetreten", *args)

class EnvironmentError(ConfigurationError):
    """Raised when there are issues with environment variables or settings."""
    def __init__(self, variable_name: str = None, *args, **kwargs):
        message = "Umgebungsvariablen-Fehler"
        if variable_name:
            message += f": {variable_name} nicht gefunden oder ungültig"
        super().__init__(message, *args)
        self.variable_name = variable_name

class SettingsValidationError(ConfigurationError):
    """Raised when settings validation fails."""
    def __init__(self, setting_name: str = None, error_detail: str = None, *args, **kwargs):
        message = "Einstellungen-Validierungsfehler"
        if setting_name:
            message += f" für {setting_name}"
        if error_detail:
            message += f": {error_detail}"
        super().__init__(message, *args)
        self.setting_name = setting_name
        self.error_detail = error_detail