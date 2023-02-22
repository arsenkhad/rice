import os

from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from db_context_manager import DBContextManager
from access import external_required
from db_work import select, select_dict, insert, call_proc
from sql_provider import SQLProvider
from datetime import date

blueprint_order = Blueprint('bp_order', __name__, template_folder='templates', static_folder='static')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/', methods=['GET', 'POST'])
def order_index():
    db_config = current_app.config['db_config']
    if request.method == 'GET':
        if session and 'rent_period' in session:
            session.pop('rent_period')
        sql = provider.get('all_items.sql')
        items = select_dict(db_config, sql)
        return render_template('catalog.html', items=items, today=date.today())
    else:
        start_date = request.form.get('start_date')
        rent_len = request.form.get('rent_len')
        if start_date and rent_len:
            session['rent_period'] = (start_date, rent_len)
            return redirect(url_for('bp_order.purchase'))
        return redirect(url_for('bp_order.order_index'))


@blueprint_order.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if session and 'rent_period' in session:
        start_date, rent_len = session['rent_period']
        start_date = date(*map(int, start_date.split('-')))
        start_date.replace(day=1)
        rent_len = int(rent_len)
        db_config = current_app.config['db_config']
        sql = provider.get('all_items.sql')
        all_items = select_dict(db_config, sql)
        if request.method == 'GET':
            available_items = available_bb(start_date, rent_len)
            items = [item for item in all_items if item['b_id'] in available_items]
            print(items)
            return render_template('catalog.html', items=items, purchase=True, sdate=start_date, rlen=rent_len)
        else:
            b_id = request.form['b_id']
            add_to_basket(b_id, all_items, start_date, rent_len)
    return redirect(url_for('bp_order.order_index'))


def available_bb(start_date, rent_len):
    db_config = current_app.config['db_config']
    _sql = provider.get('all_schedule.sql')
    schedule, _ = select(db_config, _sql)
    _sql = provider.get('all_b_id.sql')
    bb, _ = select(db_config, _sql)

    bb_list = set(line[0] for line in bb)
    end_date = get_end_date(start_date.year, start_date.month, rent_len)

    for line in schedule:
        if line[3] in bb_list:
            line_start = date(*line[:2], 1)
            line_end = get_end_date(*line[:3])
            if end_date >= line_start and start_date <= line_end:
                bb_list.discard(line[3])
    return list(bb_list)


def get_end_date(start_year, start_month, rent_len):
    end_month = (start_month + rent_len - 2) % 12 + 1
    end_year = start_year + (start_month + rent_len - 2) // 12
    return date(end_year, end_month, 1)


# Добавить проверку на пересечение по месяцам
# Переработать механизм добавления в корзину
def add_to_basket(b_id: str, items: dict, start_date, rent_len):
    item_description = [item for item in items if str(item['b_id']) == str(b_id)]
    item_description = item_description[0]
    curr_basket = session.get('basket', {})

    curr_basket[b_id] = {
        'b_id': item_description['b_id'],
        'b_adress': item_description['b_adress'],
        'b_cost': item_description['b_cost'],
        'rent_start_month': start_date.month,
        'rent_start_year': start_date.year,
        'rent_len': rent_len
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
        print(user_id, contract_num)
        o_id = save_order_with_list(current_app.config['db_config'], contract_num, current_basket)
        print(current_basket)
        if o_id:
            call_proc(current_app.config['db_config'], 'cost_update', int(o_id))
            session.pop('basket')
            return render_template('log.html', message=f'Заказ №{o_id} успешно создан')
    else:
        return render_template('log.html', message='Что-то пошло не так')


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
                    _sql4 = provider.get('insert_schedule.sql', b_id=key,
                                         start_mon=current_basket[key]['rent_start_month'],
                                         start_year=current_basket[key]['rent_start_year'],
                                         rent_len=current_basket[key]['rent_len'])
                    cursor.execute(_sql3)
                    cursor.execute(_sql4)
                return o_id


@blueprint_order.route('/clear-basket')
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(request.referrer)
