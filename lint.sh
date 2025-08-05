uv run black src
uv run black --check src

uv run isort src
uv run isort --check src

uv run ruff check src --fix
uv run ruff format src
uv run ruff check src