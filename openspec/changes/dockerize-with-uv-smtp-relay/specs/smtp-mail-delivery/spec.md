# smtp-mail-delivery Specification

## Purpose

Defines requirements for sending transactional emails (selection confirmation and reminder) via Google Workspace SMTP Relay using aiosmtplib, replacing the previous Brevo REST API integration.

## ADDED Requirements

### Requirement: SMTP Relay Connection

The mailer module SHALL connect to Google Workspace SMTP Relay at the host specified by `SMTP_HOST` (default: `smtp-relay.gmail.com`) on the port specified by `SMTP_PORT` (default: `587`) using STARTTLS encryption. The connection SHALL authenticate with `SMTP_USER` and `SMTP_PASSWORD`. The mailer SHALL NOT fall back to unencrypted connections.

#### Scenario: Successful SMTP connection

- **WHEN** `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD` are all set and valid
- **THEN** the mailer establishes a STARTTLS-encrypted connection to the SMTP server and authenticates successfully

#### Scenario: Missing credentials

- **WHEN** `SMTP_USER` or `SMTP_PASSWORD` is not set
- **THEN** the mailer logs an error and returns `False` without attempting a connection

---

### Requirement: Async Email Sending

The `send_confirmation_email` function SHALL be an `async def` coroutine using `aiosmtplib`. It SHALL NOT use `asyncio.to_thread` or any blocking SMTP library. Email sending SHALL not block the FastAPI event loop.

#### Scenario: Email sent without blocking

- **WHEN** `POST /submit` is called and triggers email sending
- **THEN** the email is sent asynchronously and the API response is returned without waiting for the SMTP connection to complete (email is awaited before response is returned, but does not block other requests)

---

### Requirement: Selection Confirmation Email

When a student successfully submits their track selection, the system SHALL send a confirmation email to the student's registered email address. The email SHALL include: student name, student ID, class number, selected track name, submission timestamp (converted to Asia/Taipei timezone), and a PDF attachment (`<student_id>_確認書.pdf`) containing the formal selection form.

#### Scenario: Confirmation email with PDF

- **WHEN** a student submits a valid track selection and `pdf_bytes` is non-empty
- **THEN** an email with subject `【重要確認信】<name> 的選填結果` is sent to the student's email with the PDF attached

#### Scenario: PDF generation failure

- **WHEN** `generate_formal_pdf` returns empty bytes or `None`
- **THEN** the API returns `{"status": "error", "message": "PDF 生成失敗"}` and no email is sent

---

### Requirement: Reminder Email

When an admin triggers the reminder function, the system SHALL send a reminder email to each student who has not yet submitted a track selection and has a registered email address. Reminder emails SHALL NOT include a PDF attachment. The system SHALL wait at least 1 second between each email send to avoid triggering SMTP rate limiting.

#### Scenario: Reminder sent to unsubmitted student

- **WHEN** admin calls `POST /admin/send-reminders` and a student has no entry in the `selections` table
- **THEN** an email with subject `【重要通知】您的類組尚未選填` is sent to that student

#### Scenario: No reminder sent to completed students

- **WHEN** a student already has a `selections` record
- **THEN** that student SHALL NOT receive a reminder email

#### Scenario: Rate limiting delay

- **WHEN** sending reminder emails to multiple students
- **THEN** the system SHALL pause at least 1 second between each email send
