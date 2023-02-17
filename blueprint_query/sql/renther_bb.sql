select b_adress, b_cost, rent_s_year, rent_start, rent_len, rent_cost
from billboards join order_line ol using(b_id)
where o_id='$input_id'