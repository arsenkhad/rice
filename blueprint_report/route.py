from flask import Blueprint, render_template

from access import login_required, group_required

blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')


@blueprint_report.route('/', methods=['GET', 'POST'])
@login_required
@group_required
def start_report():
    return render_template('menu_report.html')


@blueprint_report.route('/page1')
@group_required
def start_page1():
    return render_template('product_form.html')


@blueprint_report.route('/page2')
@group_required
def start_page2():
    return render_template('page2.html')