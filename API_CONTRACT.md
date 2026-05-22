# Kazi Mikononi API Contract

---

## 🌐 Base URL
http://localhost:5000/api

---

## 📌 RESPONSE FORMAT (STRICT)

### Success Response
{
  "success": true,
  "message": "Success",
  "data": {}
}

### Error Response
{
  "success": false,
  "message": "Error message",
  "data": null
}

---

## 🔐 AUTHENTICATION
- JWT is used
- Send token in headers:

Authorization: Bearer <token>

---

## 👥 ROLES

- client → posts jobs, hires workers
- worker → applies for jobs, performs tasks

---

## 📦 MODULES

---

### AUTH
- POST /auth/register
- POST /auth/login

---

### USERS
- GET /users/<id>
- PUT /users/<id>

---

### JOBS
- POST /jobs (client only)
- GET /jobs (public)
- GET /jobs/<id> (public)

---

### APPLICATIONS
- POST /applications (worker only)
- GET /applications/job/<job_id>

---

### MESSAGES
- POST /messages (authenticated)
- GET /messages/<conversation_id>

---

### RATINGS
- POST /ratings (client only)

---

## 🧱 PROJECT STRUCTURE RULE

Each module MUST follow:

modules/
 ├── routes.py
 ├── service.py
 ├── __init__.py

---

## ⚠️ TEAM RULES

### DO NOT:
- edit other modules
- change response format
- write business logic inside routes
- modify core files (app.py, config.py, extensions.py)

### DO:
- keep routes clean
- use service layer for logic
- follow naming conventions
- work only inside assigned module

---

## 🚀 FINAL RULE
If a feature is not in this contract, discuss before adding it.