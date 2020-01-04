"""CLI of the application"""

import typer

from api.run_server import run_server

app = typer.Typer()


@app.command()
def api(port: int = 8000, reload: bool = False):
    run_server(app="api.app.asgi:app", host="0.0.0.0", port=port, reload=reload, log_level="info")


@app.command()
def crawler():
    from crawling.run import start_process
    start_process()


if __name__ == "__main__":
    app()


