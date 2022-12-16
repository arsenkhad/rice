select b_cost, b_size, b_adress, rent_s_year, rent_start, rent_len, rent_cost
from billboards join order_line ol using(b_id)
join (select o_id from order_ where contract_num='$input_contract') d