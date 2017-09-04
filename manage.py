from __future__ import print_function
from flask_script import Manager
from application import app, db

manager = Manager(app)

@manager.command
def init_db():
    from application.models import initCourse
    db.create_all()
    initCourse()

@manager.command
def drop_db():
    db.drop_all()

if __name__ == '__main__':
    manager.run()
    # app.run(host='0.0.0.0', port=5000, debug=True)
