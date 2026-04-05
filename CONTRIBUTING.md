# Contributing to SaleFlex.PyPOS

Thank you for your interest in contributing to SaleFlex.PyPOS! We welcome all contributions,
from bug fixes and documentation improvements to new features and peripherals support.

## Ways to Contribute

- **Bug Reports** - Found a bug? Open an issue using the Bug Report template.
- **Feature Requests** - Have an idea? Open an issue using the Feature Request template.
- **Code Contributions** - Fix bugs, implement features, improve performance.
- **Documentation** - Improve or translate the docs in the docs/ folder.
- **Testing** - Help test against different databases, OS environments, or hardware.

## Getting Started

### 1. Fork and Clone

Fork the repository on GitHub, then clone your fork:

`ash
git clone https://github.com/<your-username>/SaleFlex.PyPOS.git
cd SaleFlex.PyPOS
`

### 2. Set Up the Development Environment

`ash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
`

### 3. Create a Branch

`ash
git checkout -b feature/my-feature-name
# or
git checkout -b fix/issue-description
`

### 4. Run the Application

`ash
python saleflex.py
`

## Development Guidelines

### Python Style

- Follow PEP 8.
- Use meaningful variable and function names.
- Keep functions focused and small.
- Add docstrings to public classes and methods.

### PyQt5 / UI Conventions

- All custom widgets live under user_interface/control/.
- UI forms are database-driven; avoid hardcoding layout values.
- Use the existing EventHandler and event_distributor() pattern for user actions.
- Do not mix business logic into UI widget classes.

### Database Layer

- All models live under data_layer/model/.
- Use the existing db_manager.py helper for sessions.
- Seed data belongs in data_layer/db_init_data/.
- Avoid raw SQL; use SQLAlchemy ORM queries.

### Logging and Error Handling

- Use core/logger.py for all logging (get_logger(__name__)).
- Raise SaleFlexError subclasses (defined in core/exceptions.py) for domain errors.
- Never swallow exceptions silently.

## Testing

Before submitting a pull request, please verify:

- The application starts without errors (python saleflex.py).
- The feature/fix works end-to-end in the UI.
- Existing functionality (sales, payments, closures) is not broken.
- If you added a new model, run db_initializer.py against a fresh database.

## Submitting a Pull Request

1. Push your branch to your fork.
2. Open a pull request against the main branch of SaleFlex/SaleFlex.PyPOS.
3. Fill in the pull request template completely.
4. Link any related issues (e.g. Closes #42).
5. Wait for a review — we aim to respond within a few business days.

## Bug Reports

Use the **Bug Report** issue template and include:
- Steps to reproduce the problem.
- Expected vs actual behavior.
- OS, Python version, and database backend.
- Relevant log output from logs/saleflex.log.

## Feature Requests

Use the **Feature Request** issue template and describe:
- The problem your feature solves.
- Your proposed solution and alternatives considered.
- How it fits into a typical POS workflow.

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
Please be respectful and constructive in all interactions.

## Contact

For questions not suited to a public issue, email **ferhat.mousavi@gmail.com**.

---

**Last Updated:** 2026-04-05
