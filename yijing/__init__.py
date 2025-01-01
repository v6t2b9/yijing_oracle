# yijing/__init__.py

# First, import constants
from .constants import (
    CHANGING_YIN,
    STABLE_YANG,
    STABLE_YIN,
    CHANGING_YANG
)

# First, import enums
from .enums import (
    ConsultationMode,
    LineType,
    HexagramComponent,
    ResourceType,
    LogLevel,
    ModelType,
)

# Import models
from .models import (
    Hypergram,
    HypergramData,
    HexagramContext,
    Hexagram,
    HexagramLine,
    HypergramLine
)

# Import core functionality
from .core.oracle import YijingOracle, ask_oracle
from .core.generator import cast_hypergram
from .utils.formatting import (
    generiere_erweiterte_weissagung,
    formatiere_weissagung_markdown
)

# Import settings
from .config import Settings, settings

__version__ = "0.1.0"
__author__ = "JayKay"
__license__ = "CC BY-NC 4.0"

__all__ = [
    # Core functionality
    'YijingOracle',
    'ask_oracle',
    'cast_hypergram',
    'generiere_erweiterte_weissagung',
    'formatiere_weissagung_markdown',
    'HexagramManager',

    # Models
    'Hypergram',
    'HypergramData',
    'HexagramContext',
    'Hexagram',
    'HexagramLine',
    'HypergramLine',
    
    # Enums
    'ConsultationMode',
    'LineType',
    'HexagramComponent',
    'ResourceType',
    'LogLevel',
    'ModelType',  # ModelType hinzugefügt
    
    # Configuration
    'Settings',
    'settings',
    
    # Constants
    'CHANGING_YIN',
    'STABLE_YANG',
    'STABLE_YIN',
    'CHANGING_YANG'
]