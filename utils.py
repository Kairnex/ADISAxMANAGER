from db import auth_col, warnings_col

def is_admin(user_id, chat):
    member = chat.get_member(user_id)
    return member.status in ["administrator", "creator"]

def is_sudo(user_id, sudo_users):
    return user_id in sudo_users

def is_authorized(chat_id, user_id):
    return auth_col.find_one({"chat_id": chat_id, "user_id": user_id}) is not None

def get_warning_count(chat_id, user_id):
    doc = warnings_col.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc['count'] if doc else 0

def warn_user(chat_id, user_id):
    count = get_warning_count(chat_id, user_id) + 1
    warnings_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"count": count}}, upsert=True)
    return count

def remove_warning(chat_id, user_id):
    warnings_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$inc": {"count": -1}})

def reset_warning(chat_id, user_id):
    warnings_col.delete_one({"chat_id": chat_id, "user_id": user_id})
