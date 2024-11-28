# yijing/__init__.py

# First, import constants
from .constants import (
    CHANGING_YIN,
    STABLE_YANG,
    STABLE_YIN,
    CHANGING_YANG
)

# Then import enums
from .enums import (
    ConsultationMode,
    LineType,
    HexagramComponent,
    ResourceType,
    LogLevel
)

# Import models
from .models import (
    Hypergram,
    HypergramData,
    HypergramLine,
    Hexagram,
    HexagramLine
)

# Import settings
from .settings import Settings, settings

# Finally, import oracle-related items
from .oracle import YijingOracle, ask_oracle

__version__ = "0.1.0"
__author__ = "JayKay"
__license__ = "CC BY-NC 4.0"

__all__ = [
    # Core functionality
    'YijingOracle',
    'ask_oracle',
    
    # Models
    'Hypergram',
    'HypergramData',
    'HypergramLine',
    'Hexagram',
    'HexagramLine',
    
    # Enums
    'ConsultationMode',
    'LineType',
    'HexagramComponent',
    'ResourceType',
    'LogLevel',
    
    # Configuration
    'Settings',
    'settings',
    
    # Constants
    'CHANGING_YIN',
    'STABLE_YANG',
    'STABLE_YIN',
    'CHANGING_YANG'
]