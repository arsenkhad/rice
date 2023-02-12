import os

from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from db_context_manager import DBContextManager
from access import external_required
from db_work import select_dict, insert, call_proc
from sql_provider import SQLProvider
from datetime import date

blueprint_order = Blueprint('bp_order', __name__, template_folder='templates', static_folder='static')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/', methods=['GET', 'POST'])
def order_index():
    db_config = current_app.config['db_config']
    if request.method == 'GET':
        sql = provider.get('all_items.sql')
        items = select_dict(db_config, sql)
        basket_items = session.get('basket', {})
        return render_template('catalog.html', items=items, basket=basket_items)
    else:
        b_id = request.form['b_id']
        sql = provider.get('all_items.sql')
        items = select_dict(db_config, sql)
        add_to_basket(b_id, items)
        return redirect(url_for('bp_order.order_index'))


# Добавить проверку на пересечение по месяцам
# Переработать механизм добавления в корзину
def add_to_basket(b_id: str, items: dict):
    item_description = [item for item in items if str(item['b_id']) == str(b_id)]
    item_description = item_description[0]
    curr_basket = session.get('basket', {})

    if b_id in curr_basket:
        curr_basket[b_id]['rent_len'] = curr_basket[b_id]['rent_len'] + 1
    else:
        curr_basket[b_id] = {
            'b_id': item_description['b_id'],
            'b_adress': item_description['b_adress'],
            'b_cost': item_description['b_cost'],
            'rent_start_month': date.today().month,
            'rent_start_year': date.today().year,
            'rent_len': 1
        }
        session['basket'] = curr_basket
        session.permanent = True
    return True


@blueprint_order.route('/save_order', methods=['GET', 'POST'])
@external_required
def save_order():
    user_id = session.get('user_id')
    if session.get('basket', {}):
        current_basket = session.get('basket', {})
        sql = provider.get('get_contract.sql', user_id=user_id)
        contract_num = insert(current_app.config['db_config'], sql)
        o_id = save_order_with_list(current_app.config['db_config'], contract_num, current_basket)
        print(current_basket)
        if o_id:
            call_proc(current_app.config['db_config'], 'cost_update', int(o_id))
            session.pop('basket')
            return render_template('order_created.html', o_id=o_id)
    else:
        return 'Что-то пошло не так'


def save_order_with_list(dbconfig: dict, contract_num: int, current_basket: dict):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        _sql1 = provider.get('insert_order.sql', contract_num=contract_num)
        print(_sql1)
        result1 = cursor.execute(_sql1)
        if result1 == 1:
            _sql2 = provider.get('select_order_id.sql', contract_num=contract_num)
            cursor.execute(_sql2)
            o_id = cursor.fetchall()[0][0]
            print('o_id =', o_id)
            if o_id:
                for key in current_basket:
                    print(key, current_basket[key]['rent_start_year'], current_basket[key]['rent_len'])
                    _sql3 = provider.get('insert_order_list.sql', o_id=o_id, b_id=key,
                                         start_mon=current_basket[key]['rent_start_month'],
                                         start_year=current_basket[key]['rent_start_year'],
                                         rent_len=current_basket[key]['rent_len'])
                    cursor.execute(_sql3)
                return o_id


@blueprint_order.route('/clear-basket')
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(request.referrer)