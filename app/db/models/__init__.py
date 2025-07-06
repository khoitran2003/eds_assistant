# This file makes the 'models' directory a package and allows for easier imports.
# It also helps SQLModel discover all the models when creating the database tables.

# Import order matters here to avoid circular dependency and name resolution errors.
# Models with fewer dependencies should come first.

# Base enums and types
from .general import *

# Link tables (no relationships)
from .linking import *

# Base models with no or minimal relationships
from .locations import *
from .customers import *

# Models that depend on base models
from .salons import *
from .services import *
from .artists import *
from .appointments import *
from .chat_sessions import *
