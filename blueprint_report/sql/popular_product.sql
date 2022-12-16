select prod_name, prod_price, prod_category, max(am_sum) from product
join (
    select prod_id, sum(prod_amount) am_sum from product
    join order_list using(prod_id) join user_order using(order_id)
    where year(order_date) = '$input_year'
    and month(order_date) = '$input_month'
    group by prod_id
) p using(prod_id)