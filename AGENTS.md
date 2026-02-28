# AGENTS.md instructions for

<INSTRUCTIONS>
# Repository Guidelines

## Project Structure & Module Organization
- `src/main.py` is the entry point for the proxy.
- `src/app.py`, `src/server.py`, and `src/connection.py` contain the core runtime.
- `assets/` stores images used by the README and branding.
- `blacklist.txt` and `big-blacklist.txt` are sample domain lists consumed by the proxy.
- `Dockerfile` and `blackkittenproxy.spec` define container and PyInstaller builds.
- `README.md` and `README.ru.md` document usage and features.

## Build, Test, and Development Commands
- `python src/main.py`: run the proxy from source (Python 3.8+ required, no third‑party deps).
- `python src/main.py --blacklist blacklist.txt`: run with an explicit blacklist file.
- `pip install pyinstaller` then `pyinstaller ./blackkittenproxy.spec`: build the standalone executable into `dist/`.
- `docker build -t blackkittenproxy .`: build the Docker image.
- `docker run -d --name blackkittenproxy -p 8881:8881 -v $(pwd)/blacklist.txt:/tmp/blackkittenproxy/blacklist.txt blackkittenproxy --host 127.0.0.1 --port 8881 --blacklist /tmp/blackkittenproxy/blacklist.txt --quiet`: run the containerized proxy.

## Coding Style & Naming Conventions
- Use 4‑space indentation, UTF‑8, and Python 3.8+ compatible syntax.
- Follow standard Python naming: `snake_case` for functions/variables, `CamelCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- Type hints are used in `src/*.py`; keep them consistent when adding new logic.
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


## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and file path so you can open the source for full instructions when using a specific skill.
### Available skills
- skill-creator: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations. (file: C:/Users/gryaz/.codex/skills/.system/skill-creator/SKILL.md)
- skill-installer: Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos). (file: C:/Users/gryaz/.codex/skills/.system/skill-installer/SKILL.md)
### How to use skills
- Discovery: The list above is the skills available in this session (name + description + file path). Skill bodies live on disk at the listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) When `SKILL.md` references relative paths (e.g., `scripts/foo.py`), resolve them relative to the skill directory listed above first, and only consider other paths if needed.
  3) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request; don't bulk-load everything.
  4) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks.
  5) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- Context hygiene:
  - Keep context small: summarize long sections instead of pasting them; only load extra files when needed.
  - Avoid deep reference-chasing: prefer opening only files directly linked from `SKILL.md` unless you're blocked.
  - When variants exist (frameworks, providers, domains), pick only the relevant reference file(s) and note that choice.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
</INSTRUCTIONS>
