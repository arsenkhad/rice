select b_adress, b_cost, b_size, b_quality, max(am_sum) from billboards
join (
    select b_id, sum(rent_len) am_sum from order_line
    join order_ using(o_id)
    where year(o_date) = '$input_year'
    and month(o_date) = '$input_month'
    group by b_id
) p using(b_id)