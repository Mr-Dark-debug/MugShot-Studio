# MugShot Studio API Documentation & Postman Testing Guide

This guide provides step-by-step instructions on how to test the Authentication endpoints using Postman.

**Base URL:** `http://localhost:8000` (assuming default local setup)

---

## 1. Auth Start
Checks if a user exists and determines the next step (login or signup).

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/start` 
*   **Description:** Initiates the auth flow.

**Request Body (JSON):**
```json
{
  "email": "user@example.com"
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/start`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "exists": false,
  "next": "create_account"
}
```
*(Or `exists: true` if the user is already registered)*

---

## 2. Signup
Registers a new user account.

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/signup`
*   **Description:** Creates a new user account. New users receive 100 free credits upon registration. Email confirmation is required using a 6-digit OTP code.

**Request Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "confirmPassword": "securepassword123",
  "username": "cooluser123",
  "fullName": "John Doe",
  "dob": "1990-01-01",
  "newsletterOptIn": false
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/signup`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (201 Created):**
```json
{
  "user_id": "uuid-string...",
  "message": "User created successfully. Please check your email for confirmation code.",
  "next": "confirm_email"
}
```
*Note: Users must verify their email with the 6-digit OTP code sent to their email.*

---

## 3. Verify OTP
Verifies the user's email address using the 6-digit OTP code received via email.

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/verify-otp`
*   **Description:** Confirms the email address using the OTP code.

**Request Body (JSON):**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/verify-otp`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "user_id": "uuid-string...",
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "user": { ... },
  "message": "Email verified successfully"
}
```

---

## 4. Resend Confirmation
Resends the email confirmation OTP code.

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/resend-confirmation`
*   **Description:** Triggers a new confirmation email with OTP code.

**Request Body (JSON):**
```json
{
  "email": "user@example.com"
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/resend-confirmation`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "message": "If account exists, confirmation email sent"
}
```

---

## 5. Check Username Availability
Checks if a username is available in real-time.

*   **Method:** `GET`
*   **URL:** `{{base_url}}/api/v1/auth/check-username/{username}`
*   **Description:** Checks if a username is available for registration.

**Path Parameter:**
*   `username`: The username to check

**Postman Instructions:**
1.  Set method to **GET**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/check-username/mydesiredusername`
3.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "available": true
}
```

**Error Response (409 Conflict):**
```json
{
  "detail": "Username already taken"
}
```

---

## 6. Signin
Logs in the user and returns an access token.

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/signin`
*   **Description:** Authenticates the user. Email must be confirmed.

**Request Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/signin`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "user": { ... }
}
```
*Tip: Copy the `access_token` for authenticated requests.*

---

## 7. Forgot Password
Initiates the password reset flow.

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/forgot-password`
*   **Description:** Sends a password reset link/token.

**Request Body (JSON):**
```json
{
  "email": "user@example.com"
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/forgot-password`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "message": "If account exists, reset instructions sent"
}
```

---

## 8. Reset Password
Completes the password reset process.

*   **Method:** `POST`
*   **URL:** `{{base_url}}/api/v1/auth/reset-password`
*   **Description:** Sets a new password using the reset token.

**Request Body (JSON):**
```json
{
  "token": "reset_token_from_email",
  "newPassword": "newsecurepassword123",
  "confirmPassword": "newsecurepassword123"
}
```

**Postman Instructions:**
1.  Set method to **POST**.
2.  Enter URL: `http://localhost:8000/api/v1/auth/reset-password`
3.  Go to **Body** tab -> Select **raw** -> Select **JSON**.
4.  Paste the JSON above.
5.  Click **Send**.

**Expected Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```