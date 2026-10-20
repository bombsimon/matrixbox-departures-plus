import sys, os
# The MatrixBOX 3rd party store installs the app one folder deeper (departuresplus/departuresplus).
# Run from the folder that holds the app's files, and go back afterwards.
_cwd = os.getcwd()
try: os.stat("dp_app.py")
except OSError:
    try: os.chdir("departuresplus")
    except OSError: pass
_here = os.getcwd()
_added = _here not in sys.path
if _added: sys.path.insert(0, _here)
for _m in ("code", "dp_app", "dp_web", "dp_draw", "dp_data", "dp_cfg"):
    try: del sys.modules[_m]      # older firmware keeps an app's modules cached between launches
    except Exception: pass
import ampule
ampule.routes.clear()
try:
    import code
finally:
    try: os.chdir(_cwd)
    except Exception: pass
    if _added:
        try: sys.path.remove(_here)
        except Exception: pass
