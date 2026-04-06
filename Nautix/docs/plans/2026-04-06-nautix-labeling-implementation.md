# Nautix Labeling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add simple, categorical comments to all major files in the `nautix` module to improve readability for new developers.

**Architecture:** Use high-level section labels and file-purpose headers.

**Tech Stack:** Odoo 19 (Python, XML, OWL/JS).

---

### Task 1: Module Metadata
**Files:**
- Modify: `nautix/__init__.py`
- Modify: `nautix/__manifest__.py`

**Step 1: Add labels to manifest**
(Example: `# this is the main manifest defining module metadata and dependencies`)

**Step 2: Add labels to init**
(Example: `# imports all python models for the odoo database`)

### Task 2: Core Models (Vessel & Charter)
**Files:**
- Modify: `nautix/models/vessel.py`
- Modify: `nautix/models/charter.py`

**Step 1: Label Vessel model**
(Example: `# this model stores physical specifications and availability for ships`)

**Step 2: Label Charter model**
(Example: `# this is the core chartering contract model`)

### Task 3: Support Models (Voyage, Port, Cargo, Invoice)
**Files:**
- Modify: `nautix/models/voyage.py`
- Modify: `nautix/models/port.py`
- Modify: `nautix/models/cargo_type.py`
- Modify: `nautix/models/invoice_line.py`

**Step 1: Label each model with its primary function**
(e.g., `# this model tracks individual ship journeys`)

### Task 4: AI Analysis Logic
**Files:**
- Modify: `nautix/models/ai_query.py`
- Modify: `nautix/static/src/components/ai_dashboard/ai_dashboard.js`

**Step 1: Label AI Query model**
(Example: `# this is the backend logic for processing AI logistics recommendations`)

**Step 2: Label AI Dashboard JS**
(Example: `# below are the ai chatbot frontend instructions and state management`)

### Task 5: UI Views & Data
**Files:**
- Modify: `nautix/views/views.xml`
- Modify: `nautix/data/sequences.xml`

**Step 1: Label Dashboard and Forms in XML**
(Example: `<!-- # this is the AI Dashboard client action -->`)

---
**Execution Handoff:**
Plan complete. I'll now proceed with Parallel Session execution.
