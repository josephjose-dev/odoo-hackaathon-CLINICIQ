# ClinicIQ — Intelligent Clinic Management System

🏆 **Most Promising Idea** — Odoo Buildathon 2026, BITS Pilani Dubai Campus
*(Hosted at BITS Pilani Dubai · Multi-university competition · Organised by ACM BPDC · Microsoft Tech Club · Google Developer Group)*

A smart clinic management module built on **Odoo 19** for the Odoo Buildathon 2026.
Developed under the theme: **Public & Institutional ERP**.

---

## What is ClinicIQ?

ClinicIQ is an Odoo module that unifies patient care, clinical administration, and institutional intelligence into a single platform.

It does not just track patients — it automatically scores their risk, flags critical cases before doctors arrive, and blocks dangerous prescriptions in real time.

> Built for public health institutions where speed, accuracy, and safety are non-negotiable.

---

## Features

### 1. 🔢 Auto Risk Score Engine

* Every patient receives a risk score from **0–100** computed automatically
* Formula weighs:

  * Age
  * Severity of chronic conditions
  * Missed appointments
  * Days since last visit
* Conditions are severity-weighted:

  * Severe = 15 pts
  * Moderate = 10 pts
  * Mild = 5 pts
* Score updates in real time as patient data changes

| Score Range | Risk Level  |
| ----------- | ----------- |
| 70–100      | 🔴 Critical |
| 45–69       | 🟠 High     |
| 25–44       | 🟡 Moderate |
| 0–24        | 🟢 Low      |

---

### 2. 🌙 Nightly Critical Flagging (Cron Job)

* Automated job runs every night at **midnight**
* Scans all active patients with risk score ≥ 70
* Automatically sets their state to **Critical**
* Posts a chatter message as a full audit trail
* Doctors arrive to a pre-triaged patient list every morning

---

### 3. 🚨 Real-Time Allergy Conflict Detector

* Checks prescribed medicines against patient allergies
* Raises a hard `ValidationError` if a conflict is detected
* Prescription **cannot be issued** until resolved
* Prevents dangerous prescriptions in real time

---

### 4. 📊 No-Show Probability Predictor

* Every appointment receives an automatic no-show probability score (**0–95%**)
* Based on:

  * Missed appointment history
  * Appointment type
* Emergency appointments score lower
* Routine appointments score higher
* Helps clinics optimise scheduling and reminders

---

### 5. ⏰ Overdue Checkup Flag

* Patients with no visits in over **90 days** are automatically flagged
* Visible in patient forms and list views
* Encourages proactive follow-up

---

### 6. 📋 Full Audit Trail (Chatter)

* Every important action is automatically logged
* Tracks:

  * Condition updates
  * Risk score changes
  * Prescription blocks
  * Critical status updates
* Records who made the change and when

---

## Data Models

| Model                      | Description                                     |
| -------------------------- | ----------------------------------------------- |
| `clinic.patient`           | Main patient record with risk engine            |
| `clinic.appointment`       | Appointments with no-show predictor             |
| `clinic.prescription`      | Prescriptions with allergy conflict detection   |
| `clinic.prescription.line` | Individual medicine lines                       |
| `clinic.condition`         | Chronic conditions lookup with severity weights |
| `clinic.allergy`           | Allergies lookup table                          |
| `clinic.medicine`          | Medicines lookup table                          |

---

## Demo Patients

| Patient         | Age | Conditions                       | Risk Score | Level       |
| --------------- | --- | -------------------------------- | ---------- | ----------- |
| Yousef Al-Amin  | 71  | Heart Failure, CKD, Hypertension | 80+        | 🔴 Critical |
| Ahmed Al-Rashid | 58  | Diabetes, Hypertension, Obesity  | 80+        | 🔴 Critical |
| Sara Mohammed   | 34  | Asthma                           | ~37        | 🟡 Moderate |
| Nour Al-Zahra   | 28  | None                             | ~14        | 🟢 Low      |

---


---

## Tech Stack

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Platform   | Odoo 19 (Community Edition)         |
| Backend    | Python 3.10                         |
| ORM        | Odoo ORM (PostgreSQL)               |
| Automation | Odoo Scheduled Actions (Cron Jobs)  |
| UI         | Odoo XML Views (Form, List, Kanban) |
| Validation | Python `ValidationError`            |

---

## 🏆 Awards & Recognition

ClinicIQ was awarded **Most Promising Idea** at the **Odoo Buildathon 2026**, hosted at **BITS Pilani Dubai Campus**.

The event was conducted as a **multi-university competition** in collaboration with:

* ACM BPDC
* Microsoft Tech Club
* Google Developer Group

### Certificate:

* 📜 Most Promising Idea Certificate

Certificates can be found in the ROOT folders of this repository.

---

## Project Vision

ClinicIQ demonstrates how healthcare ERP systems can evolve beyond record keeping into intelligent assistants that improve safety, efficiency, and patient outcomes.

By embedding automation and decision support directly into clinical workflows, institutions can deliver faster, safer, and more proactive care.
