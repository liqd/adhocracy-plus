# Import all signal modules to ensure they're loaded
from . import comment_signals
from . import user_signals
from . import offline_event_signals

# No register_all_signals here - it's in the main signals.py