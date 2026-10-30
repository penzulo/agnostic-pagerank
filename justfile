default:
    @just --list

# Install/sync the virtual environment
sync:
    uv sync

# Run the project CLI
run *ARGS:
    uv run agnostic-pagerank {{ARGS}}

# Format the codebase with ruff
format:
    uv run ruff format .

# Lint the codebase with ruff
lint:
    uv run ruff check .

# Lint + verify formatting without writing
check:
    uv run ruff check .
    uv run ruff format --check .

# Auto-fix lint issues and format
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run the test suite
test *ARGS:
    uv run pytest {{ARGS}}
