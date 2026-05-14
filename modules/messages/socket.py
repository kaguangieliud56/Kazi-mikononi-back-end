def get_room_name(user_id_1, user_id_2):
    return f"chat_{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}"