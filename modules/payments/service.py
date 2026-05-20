import requests
import base64
from datetime import datetime
from extensions import db
from models.transaction import Transaction
from models.job import Job
import os

def get_mpesa_token():
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
    credentials = base64.b64encode(
        f"{consumer_key}:{consumer_secret}".encode()
    ).decode("utf-8")

    response = requests.get(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {credentials}"}
    )
    return response.json().get("access_token")


def initiate_stk_push(client_id, job_id, phone_number):
    job = Job.query.get(job_id)
    if not job:
        return None, "Job not found"
    if job.client_id != client_id:
        return None, "Unauthorized"
    if job.status != "open":
        return None, "Job is not open for payment"

    token = get_mpesa_token()
    shortcode = os.getenv("MPESA_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")
    callback_url = os.getenv("MPESA_CALLBACK_URL")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{shortcode}{passkey}{timestamp}".encode()
    ).decode("utf-8")

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(job.budget),
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": f"Job{job_id}",
        "TransactionDesc": f"Payment for {job.title}"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()

    if data.get("ResponseCode") == "0":
        transaction = Transaction(
            job_id=job_id,
            client_id=client_id,
            worker_id=0,
            amount=job.budget,
            status="pending",
            checkout_request_id=data.get("CheckoutRequestID"),
            phone_number=phone_number
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction, None

    return None, data.get("errorMessage", "STK push failed")


def mpesa_callback(data):
    result = data.get("Body", {}).get("stkCallback", {})
    checkout_request_id = result.get("CheckoutRequestID")
    result_code = result.get("ResultCode")

    transaction = Transaction.query.filter_by(
        checkout_request_id=checkout_request_id
    ).first()

    if not transaction:
        return False

    if result_code == 0:
        items = result.get("CallbackMetadata", {}).get("Item", [])
        mpesa_code = next(
            (i["Value"] for i in items if i["Name"] == "MpesaReceiptNumber"), None
        )
        transaction.status = "funded"
        transaction.mpesa_code = mpesa_code

        job = Job.query.get(transaction.job_id)
        if job:
            job.status = "in_progress"
    else:
        transaction.status = "refunded"

    db.session.commit()
    return True


def release_payment(job_id, client_id):
    job = Job.query.get(job_id)
    if not job:
        return None, "Job not found"
    if job.client_id != client_id:
        return None, "Unauthorized"

    transaction = Transaction.query.filter_by(
        job_id=job_id,
        status="funded"
    ).first()

    if not transaction:
        return None, "No funded transaction found for this job"

    transaction.status = "released"
    job.status = "completed"
    db.session.commit()
    return transaction, None


def get_job_transaction(job_id, user_id):
    transaction = Transaction.query.filter_by(job_id=job_id).first()
    if not transaction:
        return None, "No transaction found"
    if transaction.client_id != user_id and transaction.worker_id != user_id:
        return None, "Unauthorized"
    return transaction, None