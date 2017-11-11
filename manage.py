from __future__ import print_function
from flask_script import Manager
from application import app, db
from scraper import getRacesfromSearchPage

manager = Manager(app)

@manager.command
def init_db():
    from application.models import initCourse
    db.create_all()
    initCourse()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def scraper_month(year, month):
    getRacesfromSearchPage({'start_year': year, 'start_mon': month, 'end_year': year, 'end_mon': month, 'jyo[]': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']})
    print('\nバックアップを取ってください。\n$ docker exec horseapi_postgres_1 pg_dumpall -U postgres > data/[ファイル名].sql')

if __name__ == '__main__':
    manager.run()
    # app.run(host='0.0.0.0', port=5000, debug=True)
