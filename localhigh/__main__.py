from .app import get_app

app = get_app()
app.run(ssl_context='adhoc', host="0.0.0.0")
