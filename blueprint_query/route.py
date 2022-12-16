import os

from flask import Blueprint, request, render_template, current_app
from access import group_required, external_required
from db_work import select
from sql_provider import SQLProvider

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_query.route('/bill_orders', methods=['GET', 'POST'])
@group_required
def bill_orders():
    if request.method == 'GET':
        return render_template('billboard_orders.html')
    else:
        input_product = request.form.get('product_name')
        if input_product:
            _sql = provider.get('billboard_orders.sql', input_product=input_product)
            product_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('db_result.html', schema=schema, result=product_result)
        else:
            return 'repeat input'


@blueprint_query.route('/renthers', methods=['GET', 'POST'])
@group_required
def renthers():
    if request.method == 'GET':
        return render_template('renther.html')
    else:
        input_renther = request.form.get('renther_name')
        if input_renther:
            _sql = provider.get('renther.sql', input_renther=input_renther)
            renther_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('db_result.html', schema=schema, result=renther_result)
        else:
            return 'repeat input'


@blueprint_query.route('/bill_info', methods=['GET', 'POST'])
@external_required
def bill_info():
    if request.method == 'GET':
        return render_template('billboard_info.html')
    else:
        input_product = request.form.get('product_name')
        if input_product:
            _sql = provider.get('billboard_info.sql', input_product=input_product)
            product_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('db_result.html', schema=schema, result=product_result)
        else:
            return 'repeat input'
