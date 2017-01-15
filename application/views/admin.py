from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from application import app, db
from application.models import Owner, Breeder, Trainer, Horse, Jockey, Horses_races, Race, Course

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
def user_list():
    return 'list'

#! データ取得(BeautifulSoup)&DB保存プログラム実装予定
@bp.route('/data', methods=['GET', 'POST'])
def add_data():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['ADMINNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_top'))
    return render_template('admin/add_data.html', error=error)
