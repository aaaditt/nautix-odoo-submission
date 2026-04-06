# Design Document: Nautix AI Command Center

## Vision
A premium, AI-driven dashboard that automates vessel matching and charter creation within Odoo. This "AI Command Center" serves as an autonomous logistics partner that handles natural language queries, evaluates fleet availability, manages complex cargo-to-ship matching, and automates database record creation.

## 1. Core Architecture (The Brain)
The backend logic will bridge natural language inputs with Odoo's `nautix.vessel` and `nautix.charter` data models.

### AI Processing Steps:
1. **Prompt Parsing**: Extracts key entities from user input (Cargo Type, Quantity in DWT, Load/Discharge Ports, Date Range).
2. **Search & Filter**: Real-time filtering of the `nautix.vessel` database based on:
    - `status == 'available'` (or becoming available within the requested date range).
    - `vessel_type` matching the cargo type requirement (e.g., Tankers for Fuel).
    - `dwt >= quantity` (or suggesting multi-ship splits).
3. **Scoring Model**: AI-driven ranking (%) based on capacity efficiency (minimizing empty space), geographical proximity (if data available), and historical fit.
4. **Tool Access**: The AI has "database writing" permissions to create/modify `nautix.charter` and `nautix.port` records via the Odoo ORM.

## 2. UI/UX Components (The Look)
A high-end, responsive dashboard built with Odoo OWL (Odoo Web Library).

### Components:
- **Command Bar (Header)**: A large, "glassmorphism" styled input field with a prominent "Scan Fleet" button. Provides a sleek, futuristic interface for natural language interaction.
- **Fleet Insights HUD**: Top-row cards showing real-time metrics:
    - Total Fleet Size.
    - Available Tankers/LNG/Bulk Carriers.
    - Capacity Utilization (%) across the fleet.
- **Vessel Recommendation Grid**: A collection of **Vessel Cards** for the top 3-5 matches.
    - **Match Score Badge**: Circular "98% Match" badge.
    - **Visual Capacity Bar**: Shows how much capacity will be consumed by the cargo.
    - **Intelligence Highlights**: Short text reasons for the match (e.g., "Nearby position", "Fuel efficient vessel").
- **Charter Preview (Sidebar)**: A slide-out panel allowing the user to review and tweak the AI-generated charter details (rates, dates, ports) before finalizing.

## 3. Workflow & Advanced Scenarios
The system handles complex operational logic beyond simple attribute matching.

- **Split-Ship Matching**: If the cargo quantity exceeds any single vessel's capacity, the AI automatically suggests a combination of 2 or more ships (e.g., "Vessel A (60k) + Vessel B (40k) for a 100k ton request").
- **Time-based Availability**: Instead of just "Currently Available," the AI evaluates ships on voyage that are scheduled to finish before the user's "Laycan Start" date.
- **Success Lifecycle**:
    1. User inputs query.
    2. AI presents recommended vessel cards.
    3. User clicks "Confirm Selection."
    4. AI creates the `nautix.charter` record, links the vessel, and populates cargo/ports.
    5. Instant redirection to the new form view with a "Success" toast notification.

## 4. Implementation Technology
- **Backend**: Python (Odoo 19), with a new `nautix.ai.query` model for tracking AI interactions.
- **Frontend**: XML/JavaScript (OWL Framework) for the dynamic dashboard and custom vessel cards.
- **AI Core**: Gemini 1.5/3 or Claude 3.5 via API integration (simulated via structured prompting for the initial version).
