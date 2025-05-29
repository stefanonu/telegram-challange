# 🚀Job Processing API (FastAPI)

A simple FastAPI project that processes unique job requests using worker assignment.

---

## 🔧 Installation

1. **Clone the repository**:

```bash
git clone <your-repo-url>
cd telegram_challange
```

2. **Install dependencies with Poetry**:

```bash
poetry install
```

3. **Initialize the database**:

```bash
poetry run python -m app.db.init_db
```

---

## ▶️ Running the API

Start the development server:

```bash
poetry run uvicorn app.main:app --reload
```

Visit the interactive docs at:  
📄 http://127.0.0.1:8000/docs

---

## 🧪 Running Tests

```bash
poetry run pytest
```