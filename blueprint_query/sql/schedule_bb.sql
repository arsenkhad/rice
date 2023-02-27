select b_adress, b_size, b_type, b_id
from schedule join billboards using (b_id)
group by b_id