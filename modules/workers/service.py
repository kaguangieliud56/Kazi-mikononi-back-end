

from extensions import db

from models.user import User
from models.skill import Skill
from models.worker_skill import WorkerSkill
from models.worker_profile import WorkerProfile
from models.worker_availability import WorkerAvailability


# =========================================================
# HELPER FUNCTION
# =========================================================
def get_worker_profile(user_id):

    return WorkerProfile.query.filter_by(
        user_id=user_id
    ).first()


# =========================================================
# CREATE OR UPDATE PROFILE
# =========================================================
def create_or_update_profile(user_id, data):

    try:

        user = User.query.get(user_id)

        if not user:
            return {
                "error": "User not found"
            }, 404

        if user.role != "worker":
            return {
                "error": "Only workers can create profiles"
            }, 403

        profile = get_worker_profile(user_id)

        # -----------------------------------------
        # CREATE PROFILE IF NOT EXISTING
        # -----------------------------------------
        if not profile:

            profile = WorkerProfile(
                user_id=user_id
            )

        # -----------------------------------------
        # UPDATE PROFILE DATA
        # -----------------------------------------
        profile.title = data.get(
            "title",
            profile.title
        )

        profile.phone = data.get(
            "phone",
            profile.phone
        )

        profile.bio = data.get(
            "bio",
            profile.bio
        )

        profile.experience_years = data.get(
            "experience_years",
            profile.experience_years
        )

        profile.hourly_rate = data.get(
            "hourly_rate",
            profile.hourly_rate
        )

        profile.profile_image = data.get(
            "profile_image",
            profile.profile_image
        )

        # -----------------------------------------
        # PROFILE COMPLETION
        # -----------------------------------------
        profile.profile_completed = True

        db.session.add(profile)

        db.session.commit()

        return {
            "message": "Profile saved successfully",
            "profile": profile.to_dict()
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "error": "Failed to save profile",
            "details": str(e)
        }, 500


# =========================================================
# GET PROFILE
# =========================================================
def get_profile(user_id):

    try:

        profile = get_worker_profile(user_id)

        if not profile:
            return {
                "error": "Profile not found"
            }, 404

        skills = WorkerSkill.query.filter_by(
            worker_id=profile.id
        ).all()

        return {
            "profile": {
                **profile.to_dict(),
                "skills": [
                    {
                        "id": ws.skill.id,
                        "name": ws.skill.name
                    }
                    for ws in skills
                ]
            }
        }, 200

    except Exception as e:

        return {
            "error": "Failed to fetch profile",
            "details": str(e)
        }, 500


# =========================================================
# ADD SKILL
# =========================================================
def add_skill_to_worker(user_id, skill_name):

    try:

        profile = get_worker_profile(user_id)

        if not profile:
            return {
                "error": "Profile not found"
            }, 404

        skill = Skill.query.filter_by(
            name=skill_name
        ).first()

        # -----------------------------------------
        # CREATE SKILL IF NOT EXIST
        # -----------------------------------------
        if not skill:

            skill = Skill(
                name=skill_name
            )

            db.session.add(skill)

            db.session.flush()

        # -----------------------------------------
        # PREVENT DUPLICATES
        # -----------------------------------------
        existing = WorkerSkill.query.filter_by(
            worker_id=profile.id,
            skill_id=skill.id
        ).first()

        if existing:
            return {
                "message": "Skill already exists"
            }, 200

        # -----------------------------------------
        # CREATE WORKER SKILL
        # -----------------------------------------
        worker_skill = WorkerSkill(
            worker_id=profile.id,
            skill_id=skill.id
        )

        db.session.add(worker_skill)

        db.session.commit()

        return {
            "message": "Skill added successfully"
        }, 201

    except Exception as e:

        db.session.rollback()

        return {
            "error": "Failed to add skill",
            "details": str(e)
        }, 500


# =========================================================
# REMOVE SKILL
# =========================================================
def remove_skill_from_worker(user_id, skill_name):

    try:

        profile = get_worker_profile(user_id)

        if not profile:
            return {
                "error": "Profile not found"
            }, 404

        skill = Skill.query.filter_by(
            name=skill_name
        ).first()

        if not skill:
            return {
                "error": "Skill not found"
            }, 404

        worker_skill = WorkerSkill.query.filter_by(
            worker_id=profile.id,
            skill_id=skill.id
        ).first()

        if not worker_skill:
            return {
                "error": "Skill not assigned"
            }, 404

        db.session.delete(worker_skill)

        db.session.commit()

        return {
            "message": "Skill removed successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "error": "Failed to remove skill",
            "details": str(e)
        }, 500


# =========================================================
# GET WORKER SKILLS
# =========================================================
def get_worker_skills(user_id):

    try:

        profile = get_worker_profile(user_id)

        if not profile:
            return {
                "error": "Profile not found"
            }, 404

        skills = WorkerSkill.query.filter_by(
            worker_id=profile.id
        ).all()

        return {
            "skills": [
                {
                    "id": ws.skill.id,
                    "name": ws.skill.name
                }
                for ws in skills
            ]
        }, 200

    except Exception as e:

        return {
            "error": "Failed to fetch skills",
            "details": str(e)
        }, 500


# =========================================================
# SET AVAILABILITY
# =========================================================
def set_availability(user_id, data):

    try:

        profile = get_worker_profile(user_id)

        if not profile:
            return {
                "error": "Profile not found"
            }, 404

        day = data.get("day_of_week")

        start = data.get("start_time")

        end = data.get("end_time")

        existing = WorkerAvailability.query.filter_by(
            worker_id=profile.id,
            day_of_week=day
        ).first()

        # -----------------------------------------
        # UPDATE EXISTING SLOT
        # -----------------------------------------
        if existing:

            existing.start_time = start

            existing.end_time = end

        # -----------------------------------------
        # CREATE NEW SLOT
        # -----------------------------------------
        else:

            new_slot = WorkerAvailability(
                worker_id=profile.id,
                day_of_week=day,
                start_time=start,
                end_time=end
            )

            db.session.add(new_slot)

        db.session.commit()

        return {
            "message": "Availability updated"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "error": "Failed to update availability",
            "details": str(e)
        }, 500


# =========================================================
# GET AVAILABILITY
# =========================================================
def get_availability(user_id):

    try:

        profile = get_worker_profile(user_id)

        if not profile:
            return {
                "error": "Profile not found"
            }, 404

        slots = WorkerAvailability.query.filter_by(
            worker_id=profile.id
        ).all()

        return {
            "availability": [
                {
                    "day": slot.day_of_week,
                    "start": slot.start_time,
                    "end": slot.end_time
                }
                for slot in slots
            ]
        }, 200

    except Exception as e:

        return {
            "error": "Failed to fetch availability",
            "details": str(e)
        }, 500


# =========================================================
# GET ALL WORKERS
# =========================================================
def get_all_workers():

    try:

        workers = User.query.filter_by(
            role="worker"
        ).all()

        workers_data = []

        for worker in workers:

            profile = get_worker_profile(worker.id)

            if not profile:
                continue

            skills = WorkerSkill.query.filter_by(
                worker_id=profile.id
            ).all()

            workers_data.append({

                # -----------------------------------------
                # USER DATA
                # -----------------------------------------
                "id": worker.id,
                "name": worker.full_name,
                "email": worker.email,
                "location": worker.location,
                "verified": worker.is_verified,

                # -----------------------------------------
                # PROFILE DATA
                # -----------------------------------------
                "title": profile.title,
                "bio": profile.bio,
                "hourly_rate": profile.hourly_rate,
                "experience_years": profile.experience_years,
                "profile_image": profile.profile_image,
                "profile_completed": profile.profile_completed,

                # -----------------------------------------
                # SKILLS
                # -----------------------------------------
                "skills": [
                    ws.skill.name
                    for ws in skills
                ]
            })

        return {
            "workers": workers_data
        }, 200

    except Exception as e:

        return {
            "error": "Failed to fetch workers",
            "details": str(e)
        }, 500