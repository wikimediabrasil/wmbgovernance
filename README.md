# WMB Governance

A digital voting and assembly management platform developed for **Wikimedia Brasil**. It enables members to participate in general assemblies, cast votes, manage proxies, and generate tamper-proof audit reports — all with LGPD-compliant data handling.

---

## Features

- **Assembly management** — create assemblies with agendas and questions
- **Voting system** — members vote on questions via radio-select interface, with support for proxy voting
- **Live results** — real-time vote tallying with separate breakdowns for senior members
- **Proxy management** — members can grant voting rights to other members for a given assembly
- **Audit log** — tamper-proof hash-chained log of all actions (votes cast, votes edited, questions opened/closed, logins)
- **Audit report** — staff can generate and download a signed JSON audit report per assembly
- **LGPD compliance** — sensitive personal data (name, email, phone, address, CPF) is encrypted at rest using field-level encryption
- **Dark mode support** — UI respects system theme preferences
- **i18n** — fully internationalised, with Portuguese (Brazil) and English support

---

## Tech Stack

- **Backend**: Django 5.x (Python)
- **Auth**: social-auth-app-django (Wikimedia OAuth)
- **Database**: SQLite (development) / MariaDB (production on Toolforge)
- **Encryption**: django-encrypted-model-fields (Fernet/AES)
- **Frontend**: W3.CSS + Font Awesome
- **i18n**: Django's built-in translation framework

---

## Requirements

- Python 3.11+
- pip

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-org/wmb_governance.git
cd wmb_governance
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```

```
SECRET_KEY=
FIELD_ENCRYPTION_KEY=
SOCIAL_AUTH_MEDIAWIKI_KEY=
SOCIAL_AUTH_MEDIAWIKI_SECRET=
```

To generate a `FIELD_ENCRYPTION_KEY`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Create a superuser**
```bash
python manage.py createsuperuser
```

**7. Run the development server**
```bash
python manage.py runserver
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `FIELD_ENCRYPTION_KEY` | Fernet key for field-level encryption of personal data |
| `SOCIAL_AUTH_MEDIAWIKI_KEY` | OAuth consumer key from Wikimedia |
| `SOCIAL_AUTH_MEDIAWIKI_SECRET` | OAuth consumer secret from Wikimedia |

> ⚠️ Never commit your `.env` file. Keep a secure backup of `FIELD_ENCRYPTION_KEY` — if lost, encrypted data is unrecoverable.

---

## Project Structure

```
wmb_governance/
├── accounts/        # Custom user model, profiles, OAuth pipeline
├── assemblies/      # Assembly, Agenda, Question, DecisionOption models and views
├── auditlog/        # Tamper-proof audit log with hash chain
├── members/         # Member, MembershipPeriod, DefaultPeriod models
├── voting/          # Vote, Proxy models, voting views and forms
├── templates/       # HTML templates
├── static/          # CSS, JS, images
└── locale/          # Translation files
```

---

## Audit Log

Every significant action is logged with a SHA-256 hash chain, making tampering detectable. Staff can download a JSON audit report per assembly from the results page.

The chain integrity is verified on every report generation and flagged in the `chain_intact` field of the exported JSON.

---

## LGPD Compliance

Personal data fields (full name, email, phone, address, postal code, CPF/RG) are encrypted at rest using AES-128 (Fernet). The encryption key is never stored in the database and must be kept secure by the administrator.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Developed by

[Wikimedia Brasil](https://wikimedia.org.br)
