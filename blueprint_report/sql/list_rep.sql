select rep_month, rep_year from rent_reports
group by rep_year, rep_month
order by rep_year, rep_month