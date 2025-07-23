# Email OTP Authentication API

A Django REST API for user login using **Email + One-Time Password (OTP)**.  
Implements **JWT tokens** for session management and includes OTP expiry, rate limiting, and mock email sending (OTP printed in terminal).

---

## **Features**

- User registration with email
- OTP request and verification
- OTP expiry (5 minutes) and rate limiting (30 seconds)
- JWT token generation for session authentication
- Mock email service (OTP printed to console)
- `.env` file for secret keys
- Docker support for containerized deployment

---

# **1. Prerequisites**

Before starting, make sure you have:

- **Python 3.10+**
- **Pip** (Python package manager)
- **Virtual environment support** (`venv`)
- **Docker** (optional, for containerized run)
- **Git** (to clone repository)

---

# **2. Clone the Repository**

```bash
git clone https://github.com/<your-username>/email_otp_auth.git
cd email_otp_auth
