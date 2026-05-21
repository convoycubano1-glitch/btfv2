from slowapi import Limiter
from slowapi.util import get_remote_address

# Module-level limiter instance shared across the app.
# Registered on app.state in main.py.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
