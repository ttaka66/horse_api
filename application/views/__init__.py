from functools import wraps
from flask import request, redirect, url_for, render_template, flash, session
from application import app, db
from application.models import Owner, Breeder, Trainer, Horse, Jockey, Horses_races, Race, Course

#! トップページ実装予定
@app.route('/')
def show_top():
    print('hello')
    return render_template('top/show_top.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['ADMINNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('admin.add_data'))
    return render_template('top/login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_top'))
