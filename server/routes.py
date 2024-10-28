# Standard Library Imports
import os

# Third Party Imports
from aiohttp import web

# Get the path to the CamApp directory (one level up from the server directory)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(ROOT)

async def index(request):
    """
    Serves the main HTML page for the application.

    :param request: The HTTP request object.
    :return: An HTTP response containing the HTML content.
    """
    with open(os.path.join(ROOT, "static", "templates", "index.html"), "r") as file:
        content = file.read()
    return web.Response(content_type="text/html", text=content)

async def javascript(request):
    """
    Serves JavaScript files for the application.

    :param request: The HTTP request object.
    :return: An HTTP response containing the JavaScript content or a 404 error.
    """
    filename = request.match_info.get('filename')
    filepath = os.path.join(ROOT, "static", "js", f"{filename}.js")
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            content = file.read()
        return web.Response(content_type="application/javascript", text=content)
    else:
        return web.Response(status=404, text="JavaScript file not found")

async def static_files(request):
    """
    Serves static files (e.g., images) for the application.

    :param request: The HTTP request object.
    :return: An HTTP response containing the file content or a 404 error.
    """
    filename = request.match_info['filename']
    path = os.path.join(ROOT, 'static', 'img', filename)
    if os.path.exists(path):
        with open(path, 'rb') as file:
            content = file.read()
        content_type = 'image/png' if filename.endswith('.png') else 'application/octet-stream'
        return web.Response(body=content, content_type=content_type)
    return web.Response(status=404)
