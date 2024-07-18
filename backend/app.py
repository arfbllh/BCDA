"""Application entrypoint."""

from core.app_factory import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False), port=4000)