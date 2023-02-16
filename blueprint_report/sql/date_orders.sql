select year(o_date) year, month(o_date) month from order_
group by year(o_date), month(o_date)