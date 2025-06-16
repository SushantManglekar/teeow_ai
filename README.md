# 🧠 Teeow AI – AI Assistant Service

This repository contains the `AI_assistant` microservice — a FastAPI app exposing endpoints for AI-powered chat functionality.

---

## 🚀 Features

- Modular FastAPI application under `AI_assistant/`
- Exposes several POST endpoints (e.g., `/chat/chat_sessions`, `chat/ask`)
- Stores conversation history in PostgreSQL
- Requires setting up a Postgres table via SQL script
- Loads database connection via `DATABASE_URL` in `.env`
- Easy local development with Uvicorn

---

## 🗂️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/SushantManglekar/teeow_ai.git
```
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
```bash
cd ./AI_assistant
```
### 2. Set up PostgreSQL
- Create a database and execute the `schema.sql` to create the schema.
- Add one user in db and copy the `user_id`

### 3. Create `.env` file 
- Create a new `.env` file in AI_assistant folder
- Add the connection string of postgresql database in this file like below
- `DATABASE_URL=YOUR_CONNECTION_STRING`

### 4. Run `llama3.2` on local system 
- Install `ollama`
- Pull the 'llama3.2` model
- Run the model by `ollama run llama3.2` and keep this running in background on CMD or Powershell.

### 5. Run the Service
```bash
uvicorn app.main:app --reload
```
### 6. Visit http://127.0.0.1:8000/docs to explore the interactive Swagger UI and test endpoints.

