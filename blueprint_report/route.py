import os
from flask import render_template, request, Blueprint, redirect, url_for, current_app
from db_work import call_proc, select, select_dict, insert
from sql_provider import SQLProvider
from access import group_required

blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_report.route('/', methods=['GET', 'POST'])
@group_required
def start_report():
    report_url = current_app.config['report_url']
    report_list = current_app.config['report_list']
    if request.method == 'GET':
        return render_template('menu_report.html', report_list=report_list, endcoding='UTF-8')
    else:
        rep_id = request.form.get('rep_id')
        if request.form.get('create_rep'):
            url_rep = report_url[rep_id]['create_rep']
        elif request.form.get('delete_rep'):
            url_rep = report_url[rep_id]['delete_rep']
        else:
            url_rep = report_url[rep_id]['view_rep']
        return redirect(url_for(url_rep))


@blueprint_report.route('/create_rep/1', methods=['GET', 'POST'])
@group_required
def create_rep1():
    if request.method == 'GET':
        return render_template('report_create.html')
    else:
        input_year = request.form.get('input_year')
        input_month = request.form.get('input_month')
        if input_year and input_month:
            _sql = provider.get('info_of_sale.sql', input_year=input_year, input_month=input_month)
            info_result = select_dict(current_app.config['db_config'], _sql)
            if len(info_result) == 0:
                return render_template('report_null.html')
            else:
                _sql = provider.get('summa_price.sql', input_month=input_month, input_year=input_year)
                product_result = select_dict(current_app.config['db_config'], _sql)
                if len(product_result) != 0:
                    return render_template('report_exists.html')
                else:
                    res = call_proc(current_app.config['db_config'], 'summ', int(input_month), int(input_year))
                    print('res = ', res)
                    return render_template('report_created.html')
        else:
            return render_template('report_create.html', message='Повторите ввод')


@blueprint_report.route('/view_rep/1', methods=['GET', 'POST'])
@group_required
def view_rep1():
    if request.method == 'GET':
        return render_template('report_create.html')
    else:
        input_year = request.form.get('input_year')
        input_month = request.form.get('input_month')
        if input_year and input_month:
            _sql = provider.get('info_of_sale.sql', input_year=input_year, input_month=input_month)
            info_result = select_dict(current_app.config['db_config'], _sql)
            if len(info_result) == 0:
                return render_template('report_null.html')
            else:
                _sql = provider.get('summa_price.sql', input_month=input_month, input_year=input_year)
                product_result, schema = select(current_app.config['db_config'], _sql)

                if len(product_result) == 0:
                    return render_template('report_not_exists.html')
                else:
                    list_name=['Сумма', 'Количество проданных товаров', 'Месяц создания отчета', 'Год создания отчета']
                    return render_template('result_1.html', schema=list_name, result=product_result)
        else:
            return render_template('report_create.html', message='Повторите ввод')


@blueprint_report.route('/delete_rep/1', methods=['GET', 'POST'])
@group_required
def delete_rep1():
    if request.method == 'GET':
        return render_template('report_create.html')
    else:
        input_year = request.form.get('input_year')
        input_month = request.form.get('input_month')
        if input_year and input_month:
            _sql = provider.get('check_for_report.sql', input_year=input_year, input_month=input_month)
            info_result = select_dict(current_app.config['db_config'], _sql)
            if len(info_result) == 0:
                return render_template('report_delete_null.html')
            else:
                _sql = provider.get('delete.sql', input_month=input_month, input_year=input_year)
                insert(current_app.config['db_config'], _sql)
                return render_template('report_deleted.html')
        else:
            return render_template('report_create.html', message='Повторите ввод')
