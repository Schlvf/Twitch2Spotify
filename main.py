import uvicorn

from API import web_app
from API.utils.env_wrapper import EnvWrapper

if __name__ == "__main__":
    """Setup web server"""

    config = uvicorn.Config(
        app=web_app.app,
        port=EnvWrapper().WEB_APP_PORT,
        host="0.0.0.0",
        log_level="info",
        reload=True,
    )
    server = uvicorn.Server(config)
    server.run()
