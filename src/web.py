import os

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles



webapp = Starlette(debug=True, routes=[
    Mount('/', app=StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "svelte-app", "public"), html=True), name="svelte"),
])