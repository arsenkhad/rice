select rep_month, rep_year, order_amount, order_sum, temp
from rent_reports
where rep_month = '$input_month' and rep_year = '$input_year'