from flask import Flask, url_for, render_template, request, json, session, redirect
from auth.route import blueprint_auth
from blueprint_query.route import blueprint_query
# from access import login_required

app = Flask(__name__)
app.secret_key = 'Pa$$w0rd'

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/requests')

app.config['db_config'] = json.load(open('data_files/dbconfig.json'))
app.config['access_config'] = json.load(open('data_files/access.json'))


@app.route('/', methods=['GET', 'POST'])
def menu_choice():
    if 'user_id' in session:
        if session.get('user_group', None):
            return render_template('internal_user_menu.html')
        else:
            return render_template('external_user_menu.html')
    else:
        return redirect(url_for('blueprint_auth.start_auth'))


@app.route('/exit')
def exit_func():
    session.clear()
    return "До свидания, заходите к нам ещё!"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
