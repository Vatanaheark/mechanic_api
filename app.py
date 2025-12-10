from app.models import db
from app import create_app

app = create_app("productionconfig")

with app.app_context():
    db.create_all()

app.run(port=5000, debug=True)