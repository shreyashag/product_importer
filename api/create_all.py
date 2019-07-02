"""
This script is used to initialise the database. Needs to be run in the application context.

For this to run correctly, the application DB needs to be accessible.
Thus, if inside docker, the script must be executed within the docker container
"""
from app import app, db

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    db.session.commit()
