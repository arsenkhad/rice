select rep_year, b_adress, b_size, b_type, b_busy, temp
from busy_reports join billboards using(b_id)
where  rep_year = '$input_year'