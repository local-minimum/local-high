from flask import Flask
from flask_login import current_user

_DOC = """<!Doctype html>
<html lang="en">
<head>
  <title>Local's Highscore as a Servish</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body>
  <h1>Local's Highscore as a Servish</h1>
  {msg}
</body>
</html>
"""

def register_routes(app: Flask):
    @app.get('/')
    def index():
        msg = ""
        if current_user.is_authenticated:
            return (
                f"<p>{current_user.name} ({current_user.email})</p>"
                '<a class="button" href="/api/logout">Logout</a>'
            )
        else:
            msg = '<a class="button" href="/api/login">Login with Evil Corp</a>'
        return _DOC.format(msg=msg) 