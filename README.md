# Offensive Security Platform

A central relational database and modular platform for offensive security and reverse engineering engagements.

## Database Schema

The platform uses a central SQLite database with the following tables:

1.  **projects**: Stores each engagement/pentest.
2.  **devices**: Stores devices tested within projects.
3.  **binaries**: Stores binaries found on devices or in firmware.
4.  **functions**: Stores functions analyzed inside binaries.
5.  **patterns**: Stores vulnerability-pattern signatures.
6.  **findings**: Stores vulnerabilities discovered.
7.  **payloads**: Stores base payloads and exploit results.
8.  **variants**: Stores morphed variants of payloads.
9.  **exploit_chains**: Stores multi-step exploit chains.
10. **sessions**: Stores active shells/implants.
11. **reports**: Stores generated reports.
12. **ai_models**: Stores connected AI models configuration.
13. **ai_analysis**: Stores AI-analysis results for code/findings.
14. **users**: Multi-user support.
15. **logs**: Audit trail for actions taken.

## Getting Started

### Prerequisites

- Python 3.12+
- SQLAlchemy

### Database Initialization

To initialize the database and create all tables:

```bash
python3 init_db.py
```

This will create an `app.db` file in the project root.

## Project Structure

- `app/database/`: Database configuration and session management.
- `app/models/`: SQLAlchemy models defining the schema.
- `init_db.py`: Database initialization script.
