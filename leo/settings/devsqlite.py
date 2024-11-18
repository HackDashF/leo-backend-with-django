from .common import *
from .dbsqlite import *

DEBUG = True

# stuff to force debug tool bar to work
def show_toolbar(request):
    return True
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}
