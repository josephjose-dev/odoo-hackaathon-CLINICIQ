# ClinicIQ — Intelligent Clinic Management System

🏆 **Most Promising Idea** — Odoo Buildathon 2026, BITS Pilani Dubai Campus
*(Hosted at BITS Pilani Dubai · Multi-university competition · Organised by ACM BPDC · Microsoft Tech Club · Google Developer Group)*

A smart clinic management module built on **Odoo 19** for the Odoo Buildathon 2026.
Developed under the theme: **Public & Institutional ERP**.

---

## What is ClinicIQ?

ClinicIQ is an Odoo module that unifies patient care, clinical administration, and institutional intelligence into a single platform. It does not just track patients — it automatically scores their risk, flags critical cases before doctors arrive, and blocks dangerous prescriptions in real time.

> Built for public health institutions where speed, accuracy, and safety are non-negotiable.

---

## Features

### 1. 🔢 Auto Risk Score Engine
- Every patient receives a risk score from **0–100** computed automatically
- Formula weighs: age + severity of chronic conditions + missed appointments + days since last visit
- Conditions are severity-weighted: Severe = 15pts · Moderate = 10pts · Mild = 5pts
- Score updates in real time as patient data changes

| Score Range | Risk Level |
|---|---|
| 70–100 | 🔴 Critical |
| 45–69 | 🟠 High |
| 25–44 | 🟡 Moderate |
| 0–24 | 🟢 Low |

---

### 2. 🌙 Nightly Critical Flagging (Cron Job)
- Automated job runs every night at **midnight**
- Scans all active patients with risk score ≥ 70
- Automatically sets their state to **Critical**
- Posts a chatter message as a full audit trail
- Doctors arrive to a **pre-triaged patient list** every morning — zero manual effort

---

### 3. 🚨 Real-Time Allergy Conflict Detector
- When a prescription is issued, the system checks every medicine against the patient's known allergies
- Raises a hard `ValidationError` if a conflict is detected
- Prescription **cannot be issued** until the conflict is resolved
- Protects patients from dangerous prescriptions in real time

---

### 4. 📊 No-Show Probability Predictor
- Every appointment gets an automatic **no-show probability score** (0–95%)
- Based on the patient's history of missed appointments and appointment type
- Emergency appointments score lower · Routine checkups score higher
- Helps clinics manage scheduling and send targeted reminders

---

### 5. ⏰ Overdue Checkup Flag
- Patients who haven't visited in over **90 days** are automatically flagged
- Visible in both the patient form and list view
- Helps clinics proactively follow up with patients who go silent

---

### 6. 📋 Full Audit Trail (Chatter)
- Every change is automatically logged — conditions added, risk score changes, prescription blocks
- Who changed what and when — zero manual effort
- Legally essential for public health institutions

---

## Data Models

| Model | Description |
|---|---|
| `clinic.patient` | Main patient record with risk engine |
| `clinic.appointment` | Appointments with no-show predictor |
| `clinic.prescription` | Prescriptions with allergy conflict detection |
| `clinic.prescription.line` | Individual medicine lines per prescription |
| `clinic.condition` | Chronic conditions lookup with severity weights |
| `clinic.allergy` | Allergies lookup table |
| `clinic.medicine` | Medicines lookup table |

---

## Demo Patients

| Patient | Age | Conditions | Risk Score | Level |
|---|---|---|---|---|
| Yousef Al-Amin | 71 | Heart Failure, CKD, Hypertension | 80+ | 🔴 Critical |
| Ahmed Al-Rashid | 58 | Diabetes, Hypertension, Obesity | 80+ | 🔴 Critical |
| Sara Mohammed | 34 | Asthma | ~37 | 🟡 Moderate |
| Nour Al-Zahra | 28 | None | ~14 | 🟢 Low |

---

## Installation

### Requirements
- Python 3.10+
- Odoo 19
- PostgreSQL 12+

### Setup Steps

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/cliniciq.git
```

**2. Place the module in your Odoo addons path**
```bash
cp -r cliniciq /path/to/odoo/addons/
```

**3. Restart Odoo and update the app list**
```bash
./odoo-bin -c odoo.conf -u clinic_iq
```

**4. Install from the Apps menu**
- Go to Apps → Search "ClinicIQ" → Install

---

## Tech Stack

| Layer | Technology |
|---|---|
| Platform | Odoo 19 (Community) |
| Backend | Python 3.10 |
| ORM | Odoo ORM (PostgreSQL) |
| Automation | Odoo Scheduled Actions (Cron) |
| UI | Odoo Views (XML) — Form, List, Kanban |
| Validation | Python `ValidationError` |

---
---

## Award

This project was awarded **Most Promising Idea** at the **Odoo Buildathon 2026**, BITS Pilani Dubai Campus (March 27 – April 7, 2026), conducted in collaboration with ACM BPDC, Microsoft Tech Club, and Google Developer Group.

---

## License

MIT License — feel free to build on this.
