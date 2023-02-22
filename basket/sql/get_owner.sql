select ow_id, ow_name from billboards join owner using(ow_id)
where b_id = '$input_id'
#may be added to catalog; currently not used