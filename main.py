import os

import uvicorn


def main():
    reload = os.getenv("APP_ENV", "production") == "development"
    uvicorn.run(
        "src.api_rest.main:app",
        host="0.0.0.0",
        port=8002,
        reload=reload,
    )


if __name__ == "__main__":
    main()
