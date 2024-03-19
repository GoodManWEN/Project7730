__name__ = 'qdata'
__version__ = '0.1.0'
__author__ = ''
__all__ = (
    'QDataClient',
    'QDataServer',
    'QDataService',
    'LoginFailedError'
)

from .client import QDataClient
from .server import QDataServer
from .service import QDataService
from .exceptions import LoginFailedError

