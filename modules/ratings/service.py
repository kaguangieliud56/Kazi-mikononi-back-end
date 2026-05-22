from extensions import db
from models.rating import Rating
from models.user import User
from models.job import Job
from models.application import Application

def submit_rating(user_id, worker_id, data):
    if user_id == worker_id:
        return None, "You cannot rate yourself"

    worker = User.query.get(worker_id)
    if not worker:
        return None, "Worker not found"
    if worker.role != "worker":
        return None, "You can only rate workers"

    score = data.get("score")
    if not score or not isinstance(score, int) or score < 1 or score > 5:
        return None, "Score must be a number between 1 and 5"

    job_id = data.get("job_id")

    existing = Rating.query.filter_by(
        user_id=user_id,
        worker_id=worker_id,
        job_id=job_id
    ).first()
    if existing:
        return None, "You have already rated this worker for this job"

    rating = Rating(
        user_id=user_id,
        worker_id=worker_id,
        job_id=job_id,
        score=score,
        comment=data.get("comment", "")
    )
    db.session.add(rating)
    db.session.commit()
    return rating, None

def submit_client_rating(user_id, client_id, data):
    if user_id == client_id:
        return None, "You cannot rate yourself"

    client = User.query.get(client_id)
    if not client:
        return None, "Client not found"
    if client.role != "client":
        return None, "You can only rate clients"

    score = data.get("score")
    if not score or not isinstance(score, int) or score < 1 or score > 5:
        return None, "Score must be a number between 1 and 5"

    job_id = data.get("job_id")

    if job_id:
        application = Application.query.filter_by(
            user_id=user_id,
            job_id=job_id,
            status="completed"
        ).first()
        if not application:
            return None, "You can only rate a client after completing a job together"

    existing = Rating.query.filter_by(
        user_id=user_id,
        worker_id=client_id,
        job_id=job_id
    ).first()
    if existing:
        return None, "You have already rated this client for this job"

    rating = Rating(
        user_id=user_id,
        worker_id=client_id,
        job_id=job_id,
        score=score,
        comment=data.get("comment", "")
    )
    db.session.add(rating)
    db.session.commit()
    return rating, None

def get_worker_ratings(worker_id):
    worker = User.query.get(worker_id)
    if not worker:
        return None, None, "Worker not found"

    ratings = Rating.query.filter_by(worker_id=worker_id).all()
    if not ratings:
        return [], 0, None

    average = round(sum(r.score for r in ratings) / len(ratings), 1)
    return ratings, average, None

def get_client_ratings(client_id):
    client = User.query.get(client_id)
    if not client:
        return None, None, "Client not found"

    ratings = Rating.query.filter_by(worker_id=client_id).all()
    if not ratings:
        return [], 0, None

    average = round(sum(r.score for r in ratings) / len(ratings), 1)
    return ratings, average, None