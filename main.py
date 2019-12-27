import typer

app = typer.Typer()

@app.command()
def api(port: int = 5000):
    from api.run import run as run_api
    run_api(port)


@app.command()
def crawler():
    from crawling.run import run as run_crawler
    run_crawler()


if __name__ == "__main__":
    app()


