import os

# Default to dev settings when importing the package directly
_dj_setting = os.environ.get('DJANGO_SETTINGS_MODULE', '')
if _dj_setting.endswith('config') or _dj_setting == '':
    from .dev import *  # noqa: F401,F403
