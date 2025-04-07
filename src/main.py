import uvicorn

from api import app
from core import EnvWrapper

if __name__ == "__main__":
    """Setup web server"""

    if EnvWrapper().ENV == "prod":
        config = uvicorn.Config(
            app=app,
            port=EnvWrapper().WEB_APP_PORT,
            host="0.0.0.0",
            log_level="info",
            reload=True,
            ssl_keyfile=EnvWrapper().SSL_KEY_FILE,
            ssl_certfile=EnvWrapper().SSL_CERT_FILE,
        )
    else:
        config = uvicorn.Config(
            app=app,
            port=EnvWrapper().WEB_APP_PORT,
            host="0.0.0.0",
            log_level="info",
            reload=True,
        )
    server = uvicorn.Server(config)
    server.run()
