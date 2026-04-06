# Design: Simple Category Comments for Nautix Module

- **Purpose**: Label all major logic and UI blocks in the `nautix` module so a stranger can understand what each part is for.
- **Approach**: Use simple `# label` comments instead of granular step-by-step documentation.

## Files to Comment
1. `__init__.py` & `__manifest__.py`: Describe the module and its dependencies.
2. `models/*.py`: Label classes, groups of fields (e.g., vessel specs), and business logic (e.g., AI analysis, status updates).
3. `views/views.xml`: Label dashboards, kanban boards, and forms (e.g., "this is the charter form view").
4. `static/src/components/ai_dashboard/*`: Label components and the AI logic.
5. `data/sequences.xml`: Label the reference number generation.

## Examples of Labels
- `# this is the vessel model used for storing ship specifications`
- `# below are the state machine methods for charter status`
- `# this is the AI prompt logic for the chatbot`
- `# these are the UI boxes for the dashboard`

## User Approval
- User approved this "simple label" approach on 2026-04-06.
