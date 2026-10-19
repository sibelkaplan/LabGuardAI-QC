You are helping build LabGuard AI, a desktop laboratory-safety application for mudlogging laboratories.

CURRENT PROJECT
- Python + PySide6 desktop app
- SQLite local database
- Entry point: app/main.py
- Design: white background, petrol blue (#0B5964), pale blue-gray (#F3F7F7), clean enterprise UI
- Languages: Turkish and English
- Initial screens: Overview, Chemical Inventory, PPE Guide, Weekly Inspections, Safety Academy, Incident Reports, Safety Assistant placeholder

YOUR TASK
1. Inspect the existing code before changing it.
2. Refactor carefully into small modules if useful; keep the app runnable after each change.
3. Implement complete Turkish/English localization using a central translation dictionary and a language selector that refreshes every visible label, form label, table header, button, placeholder, and message.
4. Improve SQLite data handling with schema migrations, validation, timestamps, and safe parameterized queries.
5. Add inventory edit/delete with confirmation, search, expiry status, quantity/unit, storage location, SDS document metadata fields, and QR identifier field (do not claim to scan QR codes unless implemented).
6. Save weekly inspection history with each item, checked/unchecked status, date, and inspector field; do not treat checkbox state as proof of physical safety.
7. Add incident history view with type, severity, description, timestamp, status, owner and corrective action.
8. Add unit tests for database operations, input validation, expiry handling, and translations.
9. Keep the white/petrol-blue design system consistent and accessible.
10. Add a clear demo/production status indicator and export/import backup for local records if feasible.

SAFETY REQUIREMENTS
- Do not invent chemical procedures, glove compatibility, respiratory protection requirements, SDS facts, or dilution quantities.
- Do not implement an HCl dilution calculator for operational use until product concentration basis, density, units, approved SOP and validation test cases are supplied by a qualified person.
- The Safety Assistant must clearly state that it is a placeholder unless connected to a curated, approved SDS/SOP knowledge base.
- If safety-critical information is missing or uncertain, advise the user to stop and consult the approved SDS/SOP and the designated safety lead.
- AI must not independently approve or authorize work; any rules engine should be deterministic, testable, and separate from generative AI.

WORKING STYLE
- First summarize the current project and propose a small implementation plan.
- Then implement one logical milestone at a time.
- Run tests and fix errors before claiming completion.
- Do not claim this is production-ready or safety-certified.
