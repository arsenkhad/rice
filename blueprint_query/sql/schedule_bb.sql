select b_adress, b_type, b_size, b_id
from schedule join billboards using (b_id)
group by b_id