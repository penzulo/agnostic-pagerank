# Agnostic PageRank: TODO

A data-agnostic PageRank library. The solver only knows about graphs; adapters convert any dataset (websites first) into a graph.

**Rule:** no website-specific logic ever enters the solver. It accepts only an edge list `(source, target, weight)` or a SciPy sparse matrix.

---

## Phase 0: Setup
- [x] Create repo and folder structure (`core/`, `adapters/`, `experiments/`, `tests/`, `data/`)
- [x] Set up virtual environment (uv + `pyproject.toml` instead of `requirements.txt`) (numpy, scipy, networkx, matplotlib, requests, beautifulsoup4, pyvis)
- [x] Write a one-paragraph README stating the goal and the 5-stage pipeline
- [x] Add `.gitignore` (ignore `data/` and crawl caches)

## Phase 1: Math Foundations (toy graphs)
- [x] Hand-build a 4-5 node graph on paper and write its adjacency matrix
- [x] Convert it to a column-stochastic matrix **M**
- [x] Add damping to form **G = d·M + (1-d)/n · J**
- [x] Solve with `numpy.linalg.eig` and extract the eigenvector for eigenvalue 1
- [x] Normalize the eigenvector so it sums to 1; this is the ground-truth rank vector
- [x] Save this toy graph and its answer as a test fixture

## Phase 2: Core Solver (`core/`)
- [x] **Graph abstraction:** class holding nodes, node-to-index mapping, and weighted directed edges
- [x] Build a CSR sparse adjacency matrix from an edge list
- [x] Column-normalize into the transition matrix
- [x] **Dangling nodes:** detect columns with no outgoing edges and redistribute their mass uniformly
- [x] **Power iteration:** `r ← d·M·r + (1-d)/n` until `||r_new - r||₁ < tol`
- [x] Config object: `damping`, `tolerance`, `max_iterations`, `personalization` (optional vector)
- [x] Return ranks plus iteration count and convergence history (needed for analysis later)
- [x] Return a ranked list of `(node, score)` sorted descending

## Phase 3: Validation
- [x] Unit test: solver output matches the dense `numpy.linalg.eig` result on the toy graph
- [x] Unit test: solver output matches `networkx.pagerank` on random graphs
- [x] Edge case tests: dangling nodes, disconnected components, self-loops, single node, empty graph
- [x] Test that ranks always sum to 1
- [x] Test that results are the same regardless of edge input order

## Phase 4: Website Adapter (`adapters/web/`)
- [ ] Crawler: start URL, BFS, stay within one domain
- [ ] Respect `robots.txt` and add a delay between requests
- [ ] Normalize URLs (strip fragments, trailing slashes, tracking params) and dedupe
- [ ] Skip non-HTML links (PDFs, images)
- [ ] Set a page cap (start at 500, then raise toward 5,000)
- [ ] Extract internal links and emit edges `(page, linked_page)`
- [ ] Cache crawled pages to disk so re-runs don't re-crawl
- [ ] Export the edge list to CSV
- [ ] Choose a target site (docs site, college site, or Wikipedia category)

## Phase 5: Public Dataset Adapter (scale test)
- [ ] Write a SNAP edge-list loader (`web-Stanford` first, ~280k nodes)
- [ ] Run the solver on it and record runtime and iteration count
- [ ] Try `web-Google` (~875k nodes) if memory allows
- [ ] Confirm results against `networkx.pagerank` on a sampled subgraph

## Phase 6: Experiments & Analysis
- [ ] Plot convergence (error vs iteration) for damping = 0.5, 0.7, 0.85, 0.95
- [ ] Plot iterations-to-converge vs graph size
- [ ] Compare power iteration time vs dense eigendecomposition on growing graphs
- [ ] Show the effect of dangling-node handling on and off
- [ ] Explain the convergence rate in terms of the second-largest eigenvalue
- [ ] Inspect the top 10 ranked pages of the crawl and sanity check them (home page, main docs, etc.)

## Phase 7: Output & Visualization
- [ ] CLI output: top-N ranked list as a table
- [ ] Export ranks to CSV
- [ ] Visualize a small subgraph (top ~50 nodes) with node size proportional to rank (`pyvis` or `networkx` + matplotlib)
- [ ] Bar chart of the top 20 pages

## Phase 8: Stretch Goals (only if time allows)
- [ ] **Personalized PageRank:** teleport to a chosen node or set of nodes
- [ ] **Second adapter:** Python import graph or citation data, to prove the "agnostic" claim
- [ ] Edge weighting options (e.g., link position or anchor text)
- [ ] Simple web UI or CLI: paste a URL, get ranked pages
- [ ] Compare against HITS or in-degree ranking

## Phase 9: Write-up & Demo
- [ ] Write the math section: Markov chain, stochastic matrix, damping, Perron-Frobenius, why power iteration converges
- [ ] Architecture diagram of the 5-stage pipeline
- [ ] Results section with plots from Phase 6
- [ ] Limitations and future work
- [ ] Final README with setup and usage instructions
- [ ] Prepare a 5-minute demo: crawl, rank, visualize

---

## Suggested Timeline
| Week | Focus |
|------|-------|
| 1 | Phases 0-3 (toy graphs, core solver, validation) |
| 2 | Phases 4-5 (crawler, SNAP loader, sparse scaling) |
| 3 | Phases 6-7 (experiments, visualization), then 8-9 (stretch and write-up) |

## Definition of Done
- [ ] Solver matches NetworkX and NumPy on all test graphs
- [ ] Runs on a 250k+ node graph in reasonable time
- [ ] Website crawl produces a sensible top-10 ranking
- [ ] Solver code contains zero website-specific logic
- [ ] README and write-up complete
