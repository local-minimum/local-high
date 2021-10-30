from .app import get_app
from .gateways import db
from routes import index, authentication

app = get_app()
db.init_app(app)
index.register_routes(app)
authentication.register_routes(app)

app.run(ssl_context='adhoc')