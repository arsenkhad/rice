select b_adress, b_cost, b_size, b_type, b_quality, b_setdate
from billboards join owner ow using(ow_id)
where ow_id='$input_id'