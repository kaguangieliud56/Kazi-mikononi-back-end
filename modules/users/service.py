from models.user import User
from extensions import db

def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location,
        "role": user.role,
        "profile_image": user.profile_image,
        "created_at": user.created_at.isoformat()
    }, None

def update_user_profile(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    user.full_name = data.get("full_name", user.full_name)
    user.phone = data.get("phone", user.phone)
    user.location = data.get("location", user.location)
    user.profile_image = data.get("profile_image", user.profile_image)

    db.session.commit()
    return user, None

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"
    db.session.delete(user)
    db.session.commit()
    return True, None
