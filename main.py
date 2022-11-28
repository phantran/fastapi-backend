import uvicorn

from core.config import config


def main():
    uvicorn.run(
        app="app.server:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True if config.ENV != "production" else False,
        workers=1,
    )


if __name__ == "__main__":
    main()
