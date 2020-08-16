import uvicorn


def run_server(**kwargs):
    uvicorn.run(**kwargs)


if __name__ == '__main__':
    from api.app.asgi import app
    run_server(app=app, host="0.0.0.0", port=9000)

