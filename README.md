# backend-common

.\.venv\Scripts\Activate
uv pip sync requirements.lock
uv pip freeze > requirements.lock


uvicorn main:app --reload