"""See README.md for package information."""

__version__ = '0.6.0'

if "bpy" in locals():
    import importlib
    importlib.reload(cli)
    importlib.reload(client)
    importlib.reload(parser)
    importlib.reload(server)
    importlib.reload(stats)
else:
    from . import cli
    from . import client
    from . import parser
    from . import server
    from . import stats
import bpy