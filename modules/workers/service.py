from models.worker_profile import WorkerProfile
from models.user import User
from models.skill import Skill
from models.worker_skill import WorkerSkill
from models.worker_availability import WorkerAvailability
from extensions import db


def create_or_update_profile(user_id, data):

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    profile = WorkerProfile.query.filter_by(user_id=user_id).first()

    # If profile doesn't exist → create it
    if not profile:
        profile = WorkerProfile(user_id=user_id)

    # Update fields (editable after signup)
    profile.title = data.get("title", profile.title)
    profile.phone = data.get("phone", user.phone)
    profile.bio = data.get("bio", profile.bio)
    profile.experience_years = data.get("experience_years", profile.experience_years)
    profile.hourly_rate = data.get("hourly_rate", profile.hourly_rate)
    profile.profile_image = data.get("profile_image", profile.profile_image)

    db.session.add(profile)
    db.session.commit()

    return {
        "message": "Profile saved successfully",
        "profile": profile.to_dict()
    }, 200


def get_profile(user_id):

    profile = WorkerProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        return {"error": "Profile not found"}, 404

    return {
        "profile": profile.to_dict()
    }, 200

def add_skill_to_worker(user_id, skill_name):

    skill = Skill.query.filter_by(name=skill_name).first()

    if not skill:
        skill = Skill(name=skill_name)
        db.session.add(skill)
        db.session.flush()

    existing = WorkerSkill.query.filter_by(
        worker_id=user_id,
        skill_id=skill.id
    ).first()

    if existing:
        return {"message": "Skill already exists"}, 200

    worker_skill = WorkerSkill(
        worker_id=user_id,
        skill_id=skill.id
    )

    db.session.add(worker_skill)
    db.session.commit()

    return {"message": "Skill added successfully"}, 201


def remove_skill_from_worker(user_id, skill_name):

    skill = Skill.query.filter_by(name=skill_name).first()

    if not skill:
        return {"error": "Skill not found"}, 404

    worker_skill = WorkerSkill.query.filter_by(
        worker_id=user_id,
        skill_id=skill.id
    ).first()

    if not worker_skill:
        return {"error": "Skill not assigned"}, 404

    db.session.delete(worker_skill)
    db.session.commit()

    return {"message": "Skill removed successfully"}, 200

def get_worker_skills(user_id):

    skills = WorkerSkill.query.filter_by(worker_id=user_id).all()

    return {
        "skills": [
            {
                "id": ws.skill.id,
                "name": ws.skill.name
            }
            for ws in skills
        ]
    }, 200

def set_availability(user_id, data):

    day = data.get("day_of_week")
    start = data.get("start_time")
    end = data.get("end_time")

    existing = WorkerAvailability.query.filter_by(
        worker_id=user_id,
        day_of_week=day
    ).first()

    if existing:
        existing.start_time = start
        existing.end_time = end
    else:
        new_slot = WorkerAvailability(
            worker_id=user_id,
            day_of_week=day,
            start_time=start,
            end_time=end
        )
        db.session.add(new_slot)

    db.session.commit()

    return {"message": "Availability updated"}, 200

def get_availability(user_id):

    slots = WorkerAvailability.query.filter_by(worker_id=user_id).all()

    return {
        "availability": [
            {
                "day": s.day_of_week,
                "start": s.start_time,
                "end": s.end_time
            }
            for s in slots
        ]
    }, 200