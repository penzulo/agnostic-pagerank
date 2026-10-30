# agnostic-pagerank

A data-agnostic PageRank library: the solver only understands graphs (edge list `(source, target, weight)` or a SciPy sparse matrix), and adapters convert any dataset into a graph. Pipeline: crawl/load → build sparse transition matrix → power iteration → ranked output → visualization.

## Layout

- `src/agnostic_pagerank/core/` — graph abstraction, transition matrix, power-iteration solver (no dataset-specific logic allowed here)
- `src/agnostic_pagerank/adapters/` — website crawler, SNAP dataset loaders
- `experiments/` — convergence/scaling analysis scripts
- `tests/` — test suite; `data/` — datasets and crawl caches (gitignored)

## Development

```sh
just sync    # uv sync
just run     # uv run agnostic-pagerank
just test    # pytest
just lint    # ruff check
just format  # ruff format
just check   # lint + format check
```

## Error-handling convention

This project uses the [`returns`](https://dry-python.github.io/returns/) library. Expected failures are values, not exceptions:

- Pure/fallible functions return `Result[T, SomeErrorEnum]` (`Success[T]` / `Failure[E]`), with errors modeled as enums (or small dataclasses), never raised.
- IO-related work returns `IOResult[T, SomeErrorEnum]`; wrap effectful calls with `@io_safe` so exceptions become `Failure` values instead of propagating.
- Compose with `.bind` / `.map` / `.lash` instead of try/except.
