import os
from flask import render_template, request, Blueprint, redirect, url_for, current_app, session
from db_work import call_proc, select, select_dict, insert
from sql_provider import SQLProvider
from access import group_required

blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


# У workerа календарик из месяцев, в котором отображается какой бб арендован в текущем
# У менеджера отчет именно о заказах!!!
@blueprint_report.route('/', methods=['GET', 'POST'])
@group_required
def start_report():
    """
    Меню работы с отчётами.
    Отображает все доступные отчёты и режимы работы с ними
    """
    report_url = current_app.config['report_url']
    report_list = current_app.config['report_list']
    access = current_app.config['access_config'][session.get('user_group', None)]
    available_report_url = [[True if report_url[report][url] in access or 'bp_report' in access else False for url in report_url[report]] for report in report_url]

    if request.method == 'GET':
        return render_template('menu_report.html', report_list=report_list, urls=available_report_url, endcoding='UTF-8')
    else:
        rep_id = request.form.get('rep_id')
        url_rep = ''
        for mode in report_url[rep_id]:
            if request.form.get(mode):
                url_rep = report_url[rep_id][mode]
        if not url_rep:
            return render_template('menu_report.html', report_list=report_list, error_message='Этот режим работы с отчетами не предусмотрен')
        return redirect(url_for(url_rep))


@blueprint_report.route('/create_rep1', methods=['GET', 'POST'])
@group_required
def create_rep1():
    _sql = provider.get('date_orders.sql')
    dates = select_dict(current_app.config['db_config'], _sql)
    years = set([date['year'] for date in dates])
    months = set([date['month'] for date in dates])
    print(*years)
    # print(*months)
    if request.method == 'GET':
        return render_template('report_create.html', dates=dates, years=years, months=months)
    else:
        input_year = request.form.get('input_year')
        input_month = request.form.get('input_month')
        if input_year and input_month:
            _sql = provider.get('sale_info.sql', input_year=input_year, input_month=input_month)
            info_result = select_dict(current_app.config['db_config'], _sql)
            if len(info_result) == 0:
                return render_template('log.html', message='Продаж в этом месяце не было')
            else:
                _sql = provider.get('rent_reports.sql', input_month=input_month, input_year=input_year)
                report_result = select_dict(current_app.config['db_config'], _sql)
                if len(report_result) != 0 and report_result[0]['temp'] == 0:
                    return render_template('log.html', message='Отчет уже существует')
                else:
                    res = call_proc(current_app.config['db_config'], 'report_sum', int(input_month), int(input_year))
                    print('res = ', res)
                    return render_template('log.html', message='Отчет создан')
        else:
            return render_template('report_create.html', dates=dates, years=years, months=months, message='Повторите ввод')


@blueprint_report.route('/view_rep1', methods=['GET', 'POST'])
@group_required
def view_rep1():
    if request.method == 'GET':
        _sql = provider.get('list_rep.sql')
        dates = select_dict(current_app.config['db_config'], _sql)
        return render_template('list_report.html', reports=dates)
    else:
        print('test')
        input_year = request.form.get('input_year')
        input_month = request.form.get('input_month')
        if input_year and input_month:
            _sql = provider.get('sale_info.sql', input_year=input_year, input_month=input_month)
            info_result = select_dict(current_app.config['db_config'], _sql)
            if len(info_result) == 0:
                return render_template('log.html', message='Продаж в этом месяце не было')
            else:
                _sql = provider.get('rent_reports.sql', input_month=input_month, input_year=input_year)
                report_result, schema = select(current_app.config['db_config'], _sql)
                if len(report_result) == 0:
                    return render_template('log.html', message='Такого отчёта пока не существует.')
                else:
                    return render_template('result_1.html', result=report_result)
        else:
            return render_template('log.html', message='Что-то пошло не так')


@blueprint_report.route('/create_rep2', methods=['GET', 'POST'])
@group_required
def create_rep2():
    return render_template('log.html', message='Что-то пошло не так')


@blueprint_report.route('/view_rep2', methods=['GET', 'POST'])
@group_required
def view_rep2():
    return render_template('log.html', message='Что-то пошло не так')
