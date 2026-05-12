from extensions import db
from models.application import Application
from models.job import Job

def apply_to_job(user_id, job_id, data):
    job = Job.query.get(job_id)
    if not job:
        return None, "Job not found"
    if job.status != "open":
        return None, "Job is not open for applications"
    
    existing = Application.query.filter_by(
        user_id=user_id, 
        job_id=job_id
    ).first()
    if existing:
        return None, "You have already applied to this job"

    application = Application(
        user_id=user_id,
        job_id=job_id,
        message=data.get("message", "")
    )
    db.session.add(application)
    db.session.commit()
    return application, None

def get_applications_for_job(job_id, client_id):
    job = Job.query.get(job_id)
    if not job:
        return None, "Job not found"
    if job.client_id != client_id:
        return None, "Unauthorized"
    applications = Application.query.filter_by(job_id=job_id).all()
    return applications, None

def update_application_status(application_id, client_id, status):
    application = Application.query.get(application_id)
    if not application:
        return None, "Application not found"
    
    job = Job.query.get(application.job_id)
    if job.client_id != client_id:
        return None, "Unauthorized"
    
    if status not in ["accepted", "rejected"]:
        return None, "Invalid status"
    
    application.status = status
    db.session.commit()
    return application, None

def get_my_applications(user_id):
    return Application.query.filter_by(user_id=user_id).all()