# Repository Guidelines

## Project Structure & Module Organization
- `src/main.py` is the single entry point and contains the proxy server, blacklist logic, and CLI handling.
- `assets/` stores images used by the README and branding.
- `blacklist.txt` and `big-blacklist.txt` are sample domain lists consumed by the proxy.
- `Dockerfile` and `nodpi.spec` define container and PyInstaller builds.
- `README.md` and `README.ru.md` document usage and features.

## Build, Test, and Development Commands
- `python src/main.py`: run the proxy from source (Python 3.8+ required, no third‑party deps).
- `python src/main.py --blacklist blacklist.txt`: run with an explicit blacklist file.
- `pip install pyinstaller` then `pyinstaller ./nodpi.spec`: build the standalone executable into `dist/`.
- `docker build -t nodpi-proxy .`: build the Docker image.
- `docker run -d --name nodpi -p 8881:8881 -v $(pwd)/blacklist.txt:/tmp/nodpi/blacklist.txt nodpi-proxy --host 127.0.0.1 --port 8881 --blacklist /tmp/nodpi/blacklist.txt --quiet`: run the containerized proxy.

## Coding Style & Naming Conventions
- Use 4‑space indentation, UTF‑8, and Python 3.8+ compatible syntax.
- Follow standard Python naming: `snake_case` for functions/variables, `CamelCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- Type hints are used in `src/main.py`; keep them consistent when adding new logic.
- No formatter or linter is configured; keep diffs minimal and readable.

## Testing Guidelines
- No automated test suite is present in this repository.
- When making changes, do a manual smoke test by running `python src/main.py` and verifying the proxy binds to `127.0.0.1:8881`.

## Commit & Pull Request Guidelines
- Git history is not available in this workspace, so no established commit convention can be inferred.
- Prefer concise, imperative commit messages (e.g., “Add SNI fragmentation fallback”).
- PRs should describe the change, list manual test steps, and note any config or CLI flag changes. Include screenshots only when UI/output text changes are user‑facing.

## Security & Configuration Tips
- Default bind address is `127.0.0.1` on port `8881`; avoid exposing the proxy publicly unless you know why.
- Keep `blacklist.txt` alongside the binary if you use `--install` autostart.
