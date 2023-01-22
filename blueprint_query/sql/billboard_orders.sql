select b_adress, rent_cost, rent_start, rent_s_year, rent_len, o_date, contract_num, r_name from order_line
join billboards using(b_id) join order_ using(o_id)
join renther using(contract_num)
where b_id='$input_id'
order by o_date