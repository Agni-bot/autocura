# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Sistema AutoCura is a Python/FastAPI application ("self-healing AI system") with modular architecture. The main entry point is `main.py` at the repo root, which starts a FastAPI/Uvicorn server on port 8000.

### Running the application

```bash
source venv/bin/activate
# Must temporarily hide /.dockerenv so the event bus connects to localhost Redis instead of autocura-redis
sudo mv /.dockerenv /.dockerenv.bak 2>/dev/null
PYTHONPATH=/workspace RELOAD=false python main.py &
sudo mv /.dockerenv.bak /.dockerenv 2>/dev/null
```

- The `/.dockerenv` workaround is needed because the Cloud VM runs inside a Docker container, and `src/core/messaging/universal_bus.py` checks for `/.dockerenv` to decide whether to connect to `autocura-redis` (Docker Compose service name) or `localhost`. By temporarily hiding it during import, the app uses `localhost`.
- Redis must be running locally on port 6379 (`sudo redis-server --daemonize yes`).
- Docker daemon must be running (`sudo dockerd &>/tmp/dockerd.log &`) because the evolution sandbox (`src/core/sandbox/evolution_sandbox.py`) connects to Docker at init time.

### Symlink requirement

The `src/__init__.py` imports from `src.services.*`, but those modules live under `backup_reorganization/src/services/`. A symlink is needed:

```bash
ln -sf ../backup_reorganization/src/services /workspace/src/services
```

### Lint, test, build commands

See `README.md` "Desenvolvimento" section for standard commands. Key ones:

- **Lint**: `flake8 main.py --max-line-length=120`, `black --check .`, `isort --check-only .`
- **Test**: `python -m pytest src/modulos/omega/tests/ -v --timeout=60`
- **Run**: `PYTHONPATH=/workspace RELOAD=false python main.py`

### Known issues in existing codebase

- Many optional services (monitoring, IA, diagnostic, ethics, guardian, security) show "not available" warnings at startup. This is expected without external API keys (e.g., `OPENAI_API_KEY`).
- Some unit tests under `backup_reorganization/tests/` fail due to missing or misaligned imports — these are pre-existing issues.
- `numpy==1.24.3` in `requirements.txt` is incompatible with Python 3.12; install `numpy>=1.26.0` instead.
- Heavy ML dependencies (TensorFlow) are not required for basic app functionality; PyTorch CPU is sufficient for tests.

### API documentation

When the server is running: Swagger UI at http://localhost:8000/docs, ReDoc at http://localhost:8000/redoc.
