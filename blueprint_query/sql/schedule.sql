select s_syear, s_smonth, s_len, b_id
from schedule
where s_syear > '$input_year' or s_syear = '$input_year' and s_smonth >= '$input_month'
order by s_syear, s_smonth