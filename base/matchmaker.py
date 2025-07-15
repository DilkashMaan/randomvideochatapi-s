waiting_users = []
 
def add_to_queue(user_id):
    if user_id not in waiting_users:
        waiting_users.append(user_id)
 
def pop_match():
    if len(waiting_users) >= 2:
        return waiting_users.pop(0), waiting_users.pop(0)
    return None, None
 
def remove_from_queue(user_id):
    if user_id in waiting_users:
        waiting_users.remove(user_id)