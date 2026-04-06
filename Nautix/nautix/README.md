# Nautix — Ship Chartering Management System

## Project Overview

**Nautix** is a custom Odoo 19 module that provides a complete ship chartering management system. It allows maritime companies to manage their fleet of vessels, create and track charter agreements (contracts to lease ships), monitor voyages, and handle hire billing — all integrated within the Odoo ERP platform.

| Detail             | Value                          |
|--------------------|--------------------------------|
| **Module Name**    | `nautix`                       |
| **Display Name**   | Nautix — Ship Chartering       |
| **Version**        | 19.0.1.0.0                     |
| **Author**         | Aadit                          |
| **License**        | LGPL-3                         |
| **Odoo Version**   | 19                             |
| **Application**    | Yes (appears in the Odoo Apps list) |

### Dependencies

| Module    | Purpose                                           |
|-----------|---------------------------------------------------|
| `base`    | Core Odoo models (partners, countries, currencies) |
| `mail`    | Message threads, followers, activity scheduling    |
| `account` | Accounting — links invoice lines to real invoices  |

---

## Models (Database Tables)

The module defines **6 models**. Each model maps to a PostgreSQL table and represents a core business entity.

---

### 1. Vessel (`nautix.vessel`)

**File:** `models/vessel.py`

Represents a ship in the fleet. Tracks physical specifications, ownership, and operational status.

**Mixins:** `mail.thread`, `mail.activity.mixin` — enables the chatter (message log) and activity scheduling on every vessel record.

| Field                  | Type               | Required | Details                                                        |
|------------------------|--------------------|----------|----------------------------------------------------------------|
| `name`                 | Char               | Yes      | Vessel name. Tracked (changes logged in chatter).              |
| `imo_number`           | Char               |          | International Maritime Organization identifier. Tracked.       |
| `vessel_type`          | Selection           |          | One of: Bulk Carrier, Tanker, Container, LNG, RoRo. Tracked.  |
| `flag_state`           | Char               |          | Country of flag registration (e.g., "Panama").                 |
| `year_built`           | Integer            |          | Year the vessel was constructed.                               |
| `dwt`                  | Float              |          | Deadweight Tonnage — total cargo + fuel + stores capacity.     |
| `grt`                  | Float              |          | Gross Registered Tonnage — internal volume measure.            |
| `loa`                  | Float              |          | Length Overall in meters.                                      |
| `beam`                 | Float              |          | Width of the vessel in meters.                                 |
| `draft`                | Float              |          | Maximum depth below waterline in meters.                       |
| `owner_id`             | Many2one → `res.partner` |   | The company that owns this vessel.                             |
| `status`               | Selection           |          | Default: `available`. Options: Available, On Charter, Under Repair, Laid Up. Tracked. |
| `classification_society` | Char             |          | Classification body (e.g., DNV, Lloyd's, ABS).                |
| `next_drydock`         | Date               |          | Scheduled drydock maintenance date.                            |

**Key behavior:** The `status` field is automatically toggled by the Charter model — when a charter is "fixed," the vessel moves to "On Charter"; when completed, it returns to "Available."

---

### 2. Port (`nautix.port`)

**File:** `models/port.py`

Represents a shipping port where cargo is loaded or discharged.

| Field        | Type                     | Required | Details                                          |
|--------------|--------------------------|----------|--------------------------------------------------|
| `name`       | Char                     | Yes      | Port name (e.g., "Singapore", "Rotterdam").      |
| `country_id` | Many2one → `res.country` |          | Country where the port is located.               |
| `unlocode`   | Char                     |          | UN/LOCODE standard code (e.g., "SGSIN").         |
| `port_type`  | Selection                |          | Dry Bulk, Liquid, Container, or General.         |

---

### 3. Cargo Type (`nautix.cargo.type`)

**File:** `models/cargo_type.py`

Master data table defining the kinds of cargo that can be shipped.

| Field       | Type      | Required | Details                                              |
|-------------|-----------|----------|------------------------------------------------------|
| `name`      | Char      | Yes      | Cargo name (e.g., "Iron Ore", "Crude Oil").          |
| `category`  | Selection |          | Dry Bulk, Liquid Bulk, Break Bulk, or Containerized. |
| `hazardous` | Boolean   |          | Whether the cargo is classified as hazardous.        |

---

### 4. Charter (`nautix.charter`)

**File:** `models/charter.py`

The **central model** of the module. Represents a charter party agreement — a contract to lease a vessel for transporting cargo.

**Mixins:** `mail.thread`, `mail.activity.mixin`

| Field                | Type                           | Required | Details                                                      |
|----------------------|--------------------------------|----------|--------------------------------------------------------------|
| `name`               | Char (readonly, copy=False)    |          | Auto-generated reference, e.g., `CHT/2024/0001`. Default: `/`. |
| `vessel_id`          | Many2one → `nautix.vessel`     | Yes      | The vessel being chartered. Tracked.                         |
| `charterer_id`       | Many2one → `res.partner`       | Yes      | The company chartering the vessel. Domain: `is_company=True`. Tracked. |
| `owner_id`           | Many2one → `res.partner`       | Yes      | The vessel owner. Tracked.                                   |
| `charter_type`       | Selection                      | Yes      | Voyage Charter, Time Charter, Bareboat, or Contract of Affreightment. Tracked. |
| `state`              | Selection                      |          | Default: `draft`. See workflow below. Tracked.               |
| `date_start`         | Date                           |          | Charter period start.                                        |
| `date_end`           | Date                           |          | Charter period end.                                          |
| `hire_rate`          | Float                          |          | Daily hire cost (used in invoice calculations).              |
| `lump_sum_freight`   | Float                          |          | One-time freight charge (for voyage charters).               |
| `currency_id`        | Many2one → `res.currency`      |          | Default: USD.                                                |
| `laycan_from`        | Date                           |          | Laycan window start (earliest vessel arrival).               |
| `laycan_to`          | Date                           |          | Laycan window end (latest vessel arrival).                   |
| `load_port_ids`      | Many2many → `nautix.port`      |          | Ports where cargo is loaded.                                 |
| `discharge_port_ids` | Many2many → `nautix.port`      |          | Ports where cargo is unloaded.                               |
| `cargo_id`           | Many2one → `nautix.cargo.type` |          | Type of cargo being transported.                             |
| `cargo_quantity`     | Float                          |          | Amount of cargo.                                             |
| `notes`              | Text                           |          | Special clauses and charter terms.                           |
| `voyage_ids`         | One2many → `nautix.voyage`     |          | All voyages under this charter.                              |
| `invoice_line_ids`   | One2many → `nautix.invoice.line` |        | Hire billing records.                                        |

#### Methods

| Method                    | What It Does                                                                 |
|---------------------------|------------------------------------------------------------------------------|
| `create()` (override)     | Auto-assigns the next sequence number (`CHT/YYYY/XXXX`) when a new charter is created. |
| `action_to_negotiation()` | Moves state from Draft → Negotiation.                                        |
| `action_fix()`            | Moves state to Fixed. **Side-effect:** Sets the vessel's status to "On Charter." |
| `action_activate()`       | Moves state to Active.                                                       |
| `action_complete()`       | Moves state to Completed. **Side-effect:** Sets the vessel's status back to "Available." |
| `action_cancel()`         | Moves state to Cancelled.                                                    |

---

### 5. Voyage (`nautix.voyage`)

**File:** `models/voyage.py`

Represents a single port-to-port leg within a charter. A charter can have multiple voyages.

| Field                | Type                       | Required | Details                                              |
|----------------------|----------------------------|----------|------------------------------------------------------|
| `charter_id`         | Many2one → `nautix.charter` | Yes     | Parent charter. `ondelete='cascade'` — deleting the charter deletes all its voyages. |
| `vessel_id`          | Many2one → `nautix.vessel` (Related) |  | Auto-populated from the charter's vessel. Read-only, stored in DB. |
| `departure_port_id`  | Many2one → `nautix.port`   |          | Port of departure.                                   |
| `arrival_port_id`    | Many2one → `nautix.port`   |          | Port of arrival.                                     |
| `etd`                | Datetime                   |          | Estimated Time of Departure.                         |
| `eta`                | Datetime                   |          | Estimated Time of Arrival.                           |
| `atd`                | Datetime                   |          | Actual Time of Departure.                            |
| `ata`                | Datetime                   |          | Actual Time of Arrival.                              |
| `status`             | Selection                  |          | Default: `planned`. Options: Planned, Underway, Completed. |

---

### 6. Invoice Line (`nautix.invoice.line`)

**File:** `models/invoice_line.py`

Billing records for hire charges. Each line represents a billing period within a charter.

| Field         | Type                         | Required | Details                                                    |
|---------------|------------------------------|----------|------------------------------------------------------------|
| `charter_id`  | Many2one → `nautix.charter`  | Yes      | Parent charter. `ondelete='cascade'`.                      |
| `period_from` | Date                         |          | Billing period start.                                      |
| `period_to`   | Date                         |          | Billing period end.                                        |
| `hire_days`   | Float (Computed, Stored)     |          | Auto-calculated: number of days between `period_from` and `period_to`. |
| `hire_rate`   | Float (Related, Stored)      |          | Pulled from `charter_id.hire_rate`. Read-only.             |
| `total_hire`  | Float (Computed, Stored)     |          | Auto-calculated: `hire_days × hire_rate`.                  |
| `invoice_id`  | Many2one → `account.move`    |          | Link to an actual Odoo accounting invoice.                 |
| `currency_id` | Many2one → `res.currency` (Related) |   | Pulled from the charter's currency.                        |

#### Computed Field Logic

- **`_compute_hire_days()`** — If both `period_from` and `period_to` are set, calculates the difference in days. Otherwise, sets to 0.
- **`_compute_total_hire()`** — Multiplies `hire_days × hire_rate`. Depends on both fields and auto-updates when either changes.

---

## Charter Workflow (State Machine)

The charter follows a linear progression with a cancel escape at any point:

```
  ┌─────────┐
  │  Draft  │
  └────┬────┘
       │  action_to_negotiation()
       ▼
 ┌─────────────┐
 │ Negotiation │
 └──────┬──────┘
        │  action_fix()
        │  ► Vessel status → "On Charter"
        ▼
   ┌─────────┐
   │  Fixed  │
   └────┬────┘
        │  action_activate()
        ▼
   ┌─────────┐
   │  Active │
   └────┬────┘
        │  action_complete()
        │  ► Vessel status → "Available"
        ▼
 ┌───────────┐
 │ Completed │
 └───────────┘

 Any state (except Completed/Cancelled)
        │  action_cancel()
        ▼
  ┌───────────┐
  │ Cancelled │
  └───────────┘
```

**Important side-effects:**
- **Fixing a charter** automatically marks the vessel as "On Charter" — preventing double-booking at a glance.
- **Completing a charter** releases the vessel back to "Available" status.

---

## Views

### Vessel Views
- **Tree (List):** Shows name, IMO, type, flag, DWT, status (color-coded badge), and owner.
- **Form:** Header with vessel name. Two column groups — "General Info" (name, IMO, type, flag, year, owner) and "Technical Specs" (DWT, GRT, LOA, beam, draft). Certification section below. Chatter at the bottom.

### Port Views
- **Tree:** Name, UN/LOCODE, country, port type.
- **Form:** Simple layout with all four fields.

### Cargo Type Views
- **Tree:** Name, category, hazardous checkbox.
- **Form:** Simple layout with all three fields.

### Charter Views (most complex)
- **Tree:** Reference, vessel, charterer, type, dates, hire rate, status badge (color-coded).
- **Kanban:** Grouped by status (columns for each state). Cards show reference, vessel, charterer, hire rate, and status badge.
- **Form:** Multi-tab layout:
  - **Header buttons** for state transitions (each only visible in the appropriate state) + a Print button for the Charter Party report.
  - **Status bar** showing the workflow progression.
  - **Tab 1 — Charter Details:** Type, vessel, charterer, owner, currency.
  - **Tab 2 — Cargo & Ports:** Cargo type/quantity, laycan dates, load ports (tag widget), discharge ports (tag widget).
  - **Tab 3 — Financials:** Hire rate, lump sum freight, start/end dates.
  - **Tab 4 — Voyages:** Inline editable list of voyage records.
  - **Tab 5 — Hire Invoices:** Inline editable list of invoice line records (computed fields are read-only).
  - **Tab 6 — Notes:** Free-text area for special clauses.
  - **Chatter** at the bottom.

### Voyage Views
- **Tree:** Charter, vessel, departure/arrival ports, ETD, ETA, status.
- **Form:** Charter and vessel (read-only), status, departure group (port, ETD, ATD), arrival group (port, ETA, ATA).

### Invoice Line Views
- **Tree:** Charter, period from/to, hire days, hire rate, total hire, invoice.
- **Form:** Charter, currency, invoice link, period dates, computed fields (read-only).

---

## Menu Structure

```
Nautix  (root menu, sequence: 10)
│
├── Fleet  (sequence: 10)
│   └── Vessels
│
├── Chartering  (sequence: 20)
│   ├── Charters
│   └── Voyages
│
├── Invoicing  (sequence: 30)
│   └── Hire Invoices
│
└── Configuration  (sequence: 90)
    ├── Ports
    └── Cargo Types
```

---

## Security & Access Control

**File:** `security/ir.model.access.csv`

All 6 models grant **full CRUD** (Create, Read, Update, Delete) access to **all internal users** (`base.group_user`):

| Access Rule                  | Model                  | Read | Write | Create | Delete |
|------------------------------|------------------------|------|-------|--------|--------|
| `access_nautix_vessel`       | `nautix.vessel`        | Yes  | Yes   | Yes    | Yes    |
| `access_nautix_port`         | `nautix.port`          | Yes  | Yes   | Yes    | Yes    |
| `access_nautix_cargo_type`   | `nautix.cargo.type`    | Yes  | Yes   | Yes    | Yes    |
| `access_nautix_charter`      | `nautix.charter`       | Yes  | Yes   | Yes    | Yes    |
| `access_nautix_voyage`       | `nautix.voyage`        | Yes  | Yes   | Yes    | Yes    |
| `access_nautix_invoice_line` | `nautix.invoice.line`  | Yes  | Yes   | Yes    | Yes    |

---

## Data & Sequences

**File:** `data/sequences.xml`

A single **IR Sequence** is defined for auto-generating charter reference numbers:

| Setting      | Value                      |
|--------------|----------------------------|
| Name         | Charter Reference          |
| Code         | `nautix.charter`           |
| Prefix       | `CHT/%(year)s/`            |
| Padding      | 4 digits                   |
| Example      | `CHT/2024/0001`            |
| Per-Company  | No (global sequence)       |

When `charter.create()` is called and the name is still `/`, Odoo fetches the next number from this sequence.

---

## Reports

**File:** `report/charter_party_report.xml`

### Charter Party Report

A **QWeb PDF report** that generates a printable charter party document. Available from the charter form view (hidden in Draft and Cancelled states).

**Report sections:**

1. **Header** — "CHARTER PARTY" title with the charter reference number.
2. **Charter Overview** — Reference, charter type, current status.
3. **Vessel Details** — Name, IMO number, vessel type, flag state, DWT.
4. **Parties** — Owner company name and Charterer company name.
5. **Dates & Laycan** — Start date, end date, laycan from/to.
6. **Financial Terms** — Currency, daily hire rate, lump sum freight.
7. **Cargo & Ports** — Cargo type, quantity, list of load ports, list of discharge ports.
8. **Special Clauses** — Contents of the notes field (only shown if populated).
9. **Signature Section** — Two-column layout with signature lines for Owner and Charterer.

Styled with Arial font, bordered tables, and a professional layout suitable for printing and physical signing.

---

## Entity Relationship Diagram

```
┌─────────────────┐        ┌─────────────────┐
│   res.partner    │        │   res.country    │
│   (Companies)    │        │                  │
└────────▲─────▲──┘        └────────▲─────────┘
         │     │                    │
   owner_id  charterer_id      country_id
         │     │                    │
┌────────┴─────┴──┐        ┌───────┴─────────┐
│  nautix.vessel   │        │   nautix.port    │
│                  │        │                  │
│ name             │        │ name             │
│ imo_number       │        │ unlocode         │
│ vessel_type      │        │ port_type        │
│ dwt, grt, loa...│        └──▲────▲──▲───▲──┘
│ status           │           │    │  │   │
└───────▲──────────┘           │    │  │   │
        │                      │    │  │   │
     vessel_id            load_ │  dis-│  dep-│  arr-
        │                port_ │ charge│ arture│ ival_
        │                 ids  │ _port │ _port │ _port
┌───────┴──────────────────────┴───┴───┴───┘───┘
│            nautix.charter                      │
│                                                │
│ name (CHT/YYYY/XXXX)                          │
│ charter_type                                   │
│ state (draft→negotiation→fixed→active→done)   │
│ hire_rate, lump_sum_freight                    │
│ date_start, date_end                           │
│ laycan_from, laycan_to                         │
│ cargo_quantity                                 │
│                                                │
│ cargo_id ──────► nautix.cargo.type             │
│                  (name, category, hazardous)    │
│                                                │
│ voyage_ids ────► nautix.voyage (One2many)      │
│ invoice_line_ids ► nautix.invoice.line (O2m)   │
└────────┬──────────────────────┬────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐   ┌──────────────────────┐
│  nautix.voyage   │   │ nautix.invoice.line   │
│                  │   │                       │
│ charter_id       │   │ charter_id            │
│ vessel_id (rel.) │   │ period_from/to        │
│ departure_port   │   │ hire_days (computed)   │
│ arrival_port     │   │ hire_rate (related)    │
│ etd, eta         │   │ total_hire (computed)  │
│ atd, ata         │   │ invoice_id → acct.move │
│ status           │   │ currency_id (related)  │
└──────────────────┘   └───────────────────────┘
```

---

## Key Features Summary

| Feature                     | Description                                                                                     |
|-----------------------------|-------------------------------------------------------------------------------------------------|
| **Fleet Management**        | Track vessels with full specs (DWT, GRT, dimensions), ownership, classification, and drydock dates. |
| **Multi-Type Charters**     | Supports Voyage, Time, Bareboat, and Contract of Affreightment charter types.                   |
| **Workflow Automation**     | State machine with buttons that progress charters through Draft → Negotiation → Fixed → Active → Completed. |
| **Vessel Status Sync**     | Vessel availability auto-updates when charters are fixed or completed.                          |
| **Voyage Tracking**        | Plan and monitor individual port-to-port legs with estimated vs. actual departure/arrival times. |
| **Hire Billing**           | Auto-calculates hire days and total cost from period dates and daily rates.                      |
| **Accounting Integration** | Invoice lines link to Odoo's `account.move` for real invoice generation.                        |
| **Multi-Currency**         | All financial fields respect the charter's selected currency.                                   |
| **Port & Cargo Master Data** | Centralized configuration with UN/LOCODE support and hazardous cargo flagging.                |
| **Charter Party Report**   | Professional PDF document with vessel details, terms, ports, and signature blocks.              |
| **Activity Tracking**      | Chatter (message log), follower subscriptions, and activity scheduling on vessels and charters.  |
| **Change Tracking**        | Key field changes are logged in the chatter (tracked fields show old → new values).             |
| **Kanban Board**           | Visual pipeline view for charters grouped by status.                                            |
| **Auto-Numbering**         | Charter references auto-generated via Odoo sequences (CHT/YYYY/XXXX format).                   |

---

## File Structure

```
Nautix/
└── nautix/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── vessel.py
    │   ├── port.py
    │   ├── cargo_type.py
    │   ├── charter.py
    │   ├── voyage.py
    │   └── invoice_line.py
    ├── views/
    │   └── views.xml          (all view definitions, actions, and menus)
    ├── security/
    │   └── ir.model.access.csv (access control rules)
    ├── data/
    │   └── sequences.xml      (charter reference sequence)
    └── report/
        └── charter_party_report.xml (QWeb PDF report template)

---

## Troubleshooting

### 1. RPC_ERROR - 404: Not Found (model `nautix.model`)

**Symptoms:** The Odoo web client fails to load or shows a 404 error when clicking on Nautix menus, referencing a model named `nautix.model`.

**Cause:** This occurs if you have previously installed a version of the module that used the generic name `nautix.model` (which has since been renamed to `nautix.charter`, `nautix.vessel`, etc.). Odoo creates database records (like menu items and window actions) that may still point to the old model name even after the code has been updated.

**Solution:** Force a module upgrade to resynchronize the database records with the current XML definitions and model registry:
```bash
python odoo-bin -u nautix -d [your_database_name] -c [your_config_file]
```

### 2. ModuleNotFoundError: No module named 'babel'

**Symptoms:** The Odoo server fails to start with a traceback ending in `ModuleNotFoundError: No module named 'babel'`.

**Cause:** Odoo 19 requires the `Babel` internationalization library, which may not be present in your local Python environment.

**Solution:** Install all required dependencies from the `requirements.txt` file in the Odoo server root:
```bash
pip install -r requirements.txt
```

### 3. Stale Frontend Assets

**Symptoms:** UI elements don't appear as expected or old menu names persist after an upgrade.

**Solution:** Perform a "Hard Refresh" in your browser (usually `Ctrl + Shift + R` or `Cmd + Shift + R`) to clear the Odoo web asset cache.
```
