# agnostic-pagerank

Data-agnostic PageRank library. `TODO.md` is the authoritative spec (phases 0–9, definitions of done); read it before starting any feature work. No README content yet — do not trust it.

## Commands

- This is a **uv** project (build backend `uv_build`, no pip/venv activation needed).
- Install/sync: `uv sync`
- Run the CLI stub: `uv run agnostic-pagerank`
- Add a dependency: `uv add <pkg>` (e.g. planned deps: numpy, scipy, networkx, matplotlib, requests, beautifulsoup4, pyvis — currently none installed)
- Requires **Python >= 3.14** (`.python-version` pins 3.14).
- Command runner is `just` (see `justfile`): `just sync|run|format|lint|check|fix|test`. Prefer `just <recipe>` over raw `uv run` commands.
- Error handling: the `returns` library. Pure fallible functions return `Result[T, ErrorEnum]`, IO work returns `IOResult[T, ErrorEnum]` (wrap effectful calls with `@io_safe`). Never raise for expected error states; compose with `.bind`/`.map`/`.lash`.

## Architecture constraints (from TODO.md)

- **The solver must contain zero website/dataset-specific logic.** Solver accepts only an edge list `(source, target, weight)` or a SciPy sparse matrix. Website-specific code belongs in `adapters/` only.
- Planned layout: `core/` (graph abstraction, sparse transition matrix, dangling-node redistribution, power iteration), `adapters/` (web crawler, SNAP loader), `experiments/`, `tests/`, `data/` (large datasets, must stay out of git).
- `src/` layout: package is `src/agnostic_pagerank/`, entry point `agnostic-pagerank = "agnostic_pagerank:main"`.
- Ranks must always sum to 1; solver must match `numpy.linalg.eig` and `networkx.pagerank` ground truth (planned test fixtures in `tests/`).

## Gotchas

- Git repo on branch `main` with **no commits yet** — everything is untracked.
- `pyproject.toml` description is still the uv placeholder.
- Planned public datasets are large (SNAP web-Stanford ~280k nodes, web-Google ~875k nodes) — use sparse matrices, not dense.
