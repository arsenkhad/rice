from flask import Flask, url_for, render_template, request, json, session, redirect
from auth.route import blueprint_auth
from basket.route import blueprint_order
from blueprint_query.route import blueprint_query, get_renther
from blueprint_report.route import blueprint_report
from access import login_required

app = Flask(__name__)
app.secret_key = 'Pa$$w0rd'

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_order, url_prefix='/order')
app.register_blueprint(blueprint_report, url_prefix='/report')
app.register_blueprint(blueprint_query, url_prefix='/query')

app.config['db_config'] = json.load(open('data_files/dbconfig.json'))
app.config['access_config'] = json.load(open('data_files/access.json'))
app.config['report_url'] = json.load(open('data_files/report_url.json'))
app.config['report_list'] = json.load(open('data_files/report_list.json', encoding='UTF-8'))


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('company.html')


@app.route('/profile')
@login_required
def profile():
    group = session.get('user_group', None)
    info = None if group else get_renther()
    print(info)
    return render_template('profile.html', login=session['login'], info=info, group=group)


@app.route('/log_out')
def log_out():
    session.clear()
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
