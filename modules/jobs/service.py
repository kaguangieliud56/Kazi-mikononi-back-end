from extensions import db
from models.job import Job

def create_job(client_id, data):
    job = Job(
        title=data["title"],
        description=data["description"],
        budget=data["budget"],
        location=data["location"],
        client_id=client_id
    )
    db.session.add(job)
    db.session.commit()
    return job

def get_all_jobs(location=None, status=None):
    query = Job.query
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Job.created_at.desc()).all()

def get_job_by_id(job_id):
    return Job.query.get(job_id)

def update_job(job_id, client_id, data):
    job = Job.query.get(job_id)
    if not job:
        return None, "Job not found"
    if job.client_id != client_id:
        return None, "Unauthorized"
    
    job.title = data.get("title", job.title)
    job.description = data.get("description", job.description)
    job.budget = data.get("budget", job.budget)
    job.location = data.get("location", job.location)
    job.status = data.get("status", job.status)

    db.session.commit()
    return job, None

def delete_job(job_id, client_id):
    job = Job.query.get(job_id)
    if not job:
        return False, "Job not found"
    if job.client_id != client_id:
        return False, "Unauthorized"
    db.session.delete(job)
    db.session.commit()
    return True, None