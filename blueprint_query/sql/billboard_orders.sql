select b_adress, rent_cost, o_date, contract_num, r_name from bill_lines
join order_ using(o_id)
join renther using(contract_num)
where b_adress='$input_product'