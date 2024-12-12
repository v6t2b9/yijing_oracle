# yijing/__init__.py

from .managers import HexagramManager

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
from .oracle import (YijingOracle,
                     ask_oracle,
                     generiere_erweiterte_weissagung,
                     formatiere_weissagung_markdown,
                     analysiere_hexagramm_eigenschaften,
                     formatiere_analyse_markdown
                    )

__version__ = "0.1.0"
__author__ = "JayKay"
__license__ = "CC BY-NC 4.0"

__all__ = [
    # Core functionality
    'YijingOracle',
    'ask_oracle',
    'generiere_erweiterte_weissagung',
    'formatiere_weissagung_markdown',
    'analysiere_hexagramm_eigenschaften',
    'formatiere_analyse_markdown',
    
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

    # HexagramManager
    'HexagramManager'
    'HexagramContext'

]