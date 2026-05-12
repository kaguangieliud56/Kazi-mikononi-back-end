from extensions import db
from models.rating import Rating
from models.user import User

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

    existing = Rating.query.filter_by(
        user_id=user_id,
        worker_id=worker_id
    ).first()
    if existing:
        return None, "You have already rated this worker"

    rating = Rating(
        user_id=user_id,
        worker_id=worker_id,
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