import os

from flask import Blueprint, request, render_template, current_app, session
from access import group_required, external_required
from db_work import select, select_dict
from sql_provider import SQLProvider
from datetime import date

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

title_bb = ['Адрес', 'Стоимость в месяц', 'Размер', 'Тип', 'Качество', 'Дата установки']


@blueprint_query.route('/bill_owners', methods=['GET', 'POST'])
@group_required
def bill_owners():
    if request.method == 'GET':
        _sql = provider.get('owner_all.sql')
        owners, _ = select(current_app.config['db_config'], _sql)
        return render_template('all_owners.html', owners=owners)
    else:
        _id = request.form.get('ow_id')
        _sql = provider.get('owner_info.sql', input_id=_id)
        owner, _ = select(current_app.config['db_config'], _sql)
        _sql = provider.get('owner_bb.sql', input_id=_id)
        billboards, _ = select(current_app.config['db_config'], _sql)
        return render_template('owner_billboards.html', owner=owner[0], result=billboards, schema=title_bb)


@blueprint_query.route('/schedule')
@group_required
def view_schedule():
    today = date.today()
    _sql = provider.get('schedule.sql', input_year=today.year, input_month=today.month)
    schedule, _ = select(current_app.config['db_config'], _sql)
    _sql = provider.get('schedule_bb.sql')
    bb, _ = select(current_app.config['db_config'], _sql)
    bb = {line[-1]: line[:-1] for line in bb}
    out_schedule = []
    for line in schedule:
        for i in range(line[2]):
            out_schedule.append([line[0]+(line[1]+i-1) // 12, (line[1]+i-1) % 12 + 1, line[3]])
    schedule = {year: {f'{date.today().replace(month=month):%B}': [line[-1] for line in out_schedule if line[0] == year and line[1] == month]
                for month in sorted(list(set([line[1] for line in out_schedule if line[0] == year])))}
                for year in sorted(list(set(line[0] for line in out_schedule)))}
    print(schedule)
    return render_template('schedule.html', schedule=schedule, schema=[title_bb[i] for i in [0, 3, 2]], bb=bb)


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


@blueprint_query.route('/renther_history')
@external_required
def renther_history():
    _sql = provider.get('get_contract.sql', input_user=session['user_id'])
    result = select(current_app.config['db_config'], _sql)[0][0][0]
    if result:
        return get_orders(result, 'Вы не сделали ни одного заказа')
    else:
        return render_template('log.html', message='Что-то пошло не так')
    # messages=['Это гостевой аккаунт.', '''Для просмотра
    #                    истории заказов попросите администратора
    #                    привязать ваш номер договора''']


def get_orders(_id, errtxt, show=False):
    _sql = provider.get('renther_orders.sql', input_contract=_id)
    orders, _ = select(current_app.config['db_config'], _sql)
    info = get_renther(_id) if show else []
    lines = []
    for order in orders:
        _sql = provider.get('renther_bb.sql', input_id=order[0])
        line, _ = select(current_app.config['db_config'], _sql)
        lines.append(line)
    title = ['Адрес билборда', 'Стоимость в месяц', 'Год начала аренды', 'Месяц начала аренды', 'Длительность аренды', 'Общая стоимость']
    return render_template('renther_history.html', orders=orders, lines=lines, schema=title, info=info, message=errtxt)


def get_renther(_id=None):
    if not _id:
        _sql = provider.get('get_contract.sql', input_user=session['user_id'])
        _id = select(current_app.config['db_config'], _sql)[0][0][0]
    _sql = provider.get('renther_info.sql', input_id=_id)
    r_data, r_head = select(current_app.config['db_config'], _sql)
    r_info = dict(zip(r_head, *r_data))
    print(r_info)
    return r_info
