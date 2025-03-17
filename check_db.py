from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    print("Columns in user table:")
    for column in inspector.get_columns('user'):
        print(f"- {column['name']}: {column['type']}") 