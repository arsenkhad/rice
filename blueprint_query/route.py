import os

from flask import Blueprint, request, render_template, current_app, session
from access import group_required, external_required
from db_work import select
from sql_provider import SQLProvider

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


# to be transformed to a report
@blueprint_query.route('/bill_orders', methods=['GET', 'POST'])
@group_required
def bill_orders():
    if request.method == 'GET':
        return render_template('request.html', rq_line="ID билборда", rq_placeholder="ID")
    else:
        input_id = request.form.get('input_get')
        if input_id:
            _sql = provider.get('billboard_orders.sql', input_id=input_id)
            orders, schema = select(current_app.config['db_config'], _sql)
            if len(orders):
                return render_template('table.html', schema=schema, result=orders, render=True)
            _sql = provider.get('billboard_info.sql', input_id=input_id)
            bb_info, _ = select(current_app.config['db_config'], _sql)
            if len(bb_info):
                return render_template('renther_menu.html', messages=['На этот биллборд нет заказов'])
            return render_template('renther_menu.html', messages=['Такого биллборда нет'])
        else:
            return render_template('request.html', message='Повторите ввод')


@blueprint_query.route('/renther_orders', methods=['GET', 'POST'])
@group_required
def renther_history_all():
    if request.method == 'GET':
        _sql = provider.get('renther_all.sql')
        renthers, _ = select(current_app.config['db_config'], _sql)
        return render_template('choose_renther.html', renthers=renthers)
    else:
        _id = request.form.get('history_id')
        return get_orders(_id, 'Нет заказов', show=True)


@blueprint_query.route('/renther_history', methods=['GET', 'POST'])
@external_required
def renther_history():
    _sql = provider.get('get_contract.sql', input_user=session['user_id'])
    result = select(current_app.config['db_config'], _sql)[0][0][0]
    if result:
        return get_orders(result, 'Вы не сделали ни одного заказа')
    else:
        return render_template('renther_menu.html',
                           messages=['Это гостевой аккаунт.', '''Для просмотра
                                              истории заказов попросите администратора
                                              привязать ваш номер договора'''])


def get_orders(_id, errtxt, show=False):
    _sql = provider.get('renther_orders.sql', input_contract=_id)
    orders, schema = select(current_app.config['db_config'], _sql)
    lines = []
    if len(orders):
        for order in orders:
            _sql = provider.get('renther_bb.sql', input_id=order[0])
            line, schema = select(current_app.config['db_config'], _sql)
            lines.append(line)
        info = get_renther(_id) if show else []
        return render_template('renther_history.html', orders=orders, lines=lines, schema=schema, info=info)
    return render_template('renther_menu.html', messages=[errtxt])


def get_renther(_id):
    _sql = provider.get('renther_info.sql', input_id=_id)
    r_data, r_head = select(current_app.config['db_config'], _sql)
    r_info = dict(zip(r_head, *r_data))
    print(r_info)
    return r_info
