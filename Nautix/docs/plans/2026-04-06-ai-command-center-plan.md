# [Nautix AI Command Center] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a premium AI-driven dashboard for vessel matching and automated charter creation in Odoo 19.

**Architecture:** A custom Odoo Client Action (OWL) that communicates with a specialized `nautix.ai.query` backend model. The backend parses natural language using a simulated AI logic (to be replaced with a live API later) and performs Odoo ORM searches to find optimal vessel matches.

**Tech Stack:** Python (Odoo 19), JavaScript (OWL Framework), XML (Odoo Views), CSS (Vanilla).

---

### Task 1: AI Query Data Model
Store the prompts and the structured results from the AI analysis.

**Files:**
- Create: `Nautix/nautix/models/ai_query.py`
- Modify: `Nautix/nautix/models/__init__.py`
- Modify: `Nautix/nautix/__manifest__.py`

**Step 1: Implement the model**
```python
from odoo import models, fields, api

class NautixAIQuery(models.Model):
    _name = 'nautix.ai.query'
    _description = 'Nautix AI Query'

    prompt = fields.Text(string='User Prompt', required=True)
    results_json = fields.Text(string='AI Analysis Result')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('failed', 'Failed')
    ], default='draft')
    charter_id = fields.Many2one('nautix.charter', string='Created Charter')
```

**Step 2: Register in __init__.py**
```python
from . import ai_query
```

**Step 3: Update manifest**
Ensure the new model file is recognized.

---

### Task 2: AI Logic & Vessel Matching
The "Brain" that translates text into fleet queries.

**Files:**
- Modify: `Nautix/nautix/models/ai_query.py`

**Step 1: Implement `action_analyze` method**
- Parse prompt for: Cargo Type, Quantity (tons), Date.
- Search `nautix.vessel` for matching types and available status.
- Filter by DWT capacity.
- Return a JSON list of matches with "Match Score".

---

### Task 3: OWL Dashboard Frontend
Create the premium "Command Center" UI.

**Files:**
- Create: `Nautix/nautix/static/src/components/ai_dashboard/ai_dashboard.js`
- Create: `Nautix/nautix/static/src/components/ai_dashboard/ai_dashboard.xml`
- Create: `Nautix/nautix/static/src/components/ai_dashboard/ai_dashboard.scss`

**Step 1: XML Template**
- Header with high-style Glassmorphism input.
- Stats HUD (HUD cards).
- Results Grid (Vessel Cards).

**Step 2: JS Component Logic**
- State management for search queries.
- RPC calls to `nautix.ai.query`.
- Loading overlays.

---

### Task 4: Charter Creation Workflow
The "Agentic" part: committing the AI's choice to the database.

**Files:**
- Modify: `Nautix/nautix/models/ai_query.py`

**Step 1: Implement `create_charter_from_match`**
- Takes vessel_id and parsed details.
- Calls `nautix.charter`.create() with pre-filled ports and dates.
- Returns the new record ID for UI redirection.

---

### Task 5: Odoo Navigation & Menus
**Files:**
- Modify: `Nautix/nautix/views/views.xml`

**Step 1: Add Client Action**
Register the component as a reachable menu item "Nautix AI".
