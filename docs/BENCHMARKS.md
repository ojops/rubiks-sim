# Controlled solver comparison

Run from the repository root:

```bash
uv sync --locked
uv run python benchmarks/solver.py --repeats 2
```

The [recorded JSONL](../benchmarks/results/coordinate-heuristic.jsonl) contains every scramble, seed, limit, solution, verification result, bound, node count, and timing. This run used Python 3.10.22 on Linux-6.18.57-x86_64-with-glibc2.41 (through WSL). Each solve had depth 10, 100,000 visited nodes and five seconds. Both heuristics used the same cubie model, move order, and pruning. Two repetitions alternate heuristic order, times below are medians, not statistical performance estimates.

Cold pattern table construction took **0.690 seconds**, retaining 44,555 distance bytes. It is reported separately before the benchmark's warm searches, normal `solve` and CLI budgets include cold setup. A separate CLI process rebuilds its tables. The basic heuristic needs no table setup.

| Scramble length / seed | Basic status | Basic nodes | Basic seconds | Pattern status | Pattern nodes | Pattern seconds | Solution depth |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 4 / 0 | solved | 453 | 0.0045 | solved | 29 | 0.0005 | 4 |
| 5 / 0 | solved | 5,057 | 0.0485 | solved | 42 | 0.0007 | 5 |
| 6 / 0 | solved | 81,213 | 0.7637 | solved | 1,777 | 0.0274 | 6 |
| 7 / 0 | solved | 11,449 | 0.1100 | solved | 103 | 0.0016 | 5 |
| 8 / 0 | solved | 44,571 | 0.4275 | solved | 243 | 0.0038 | 6 |
| 8 / 1 | node_limit | 100,000 | 0.9491 | solved | 13,308 | 0.2051 | 7 |
| 8 / 2 | node_limit | 100,000 | 0.9368 | solved | 12,585 | 0.1916 | 7 |
| 10 / 0 | node_limit | 100,000 | 0.9600 | solved | 49,506 | 0.7701 | 8 |
| 10 / 1 | node_limit | 100,000 | 0.9532 | node_limit | 100,000 | 1.5428 | — |
| 20 / 42 | node_limit | 100,000 | 0.9657 | node_limit | 100,000 | 1.5560 | — |

All returned solutions were independently replayed on the sticker model. Where both solvers finished, optimal solution depths agree. Seven and eight move generated sequences can simplify to shorter solutions, input length is **not** search depth.

The six move case reduced visited nodes from 81,213 to 1,777 (about 46 times fewer) and warm time from about 0.76 to 0.03 seconds. The pattern solver also completed two seven move optimal solutions and one eight move optimal solution that exhausted the original solver's node budget. These are measured cases, not a guarantee for all scrambles at those depths.

The ten move seed-1 and twenty move seed-42 cases still exhausted both node budgets. Pattern evaluation made those 100,000 node failures slower despite reaching higher search bounds. Cold setup also makes tiny one off solves slower than their warm numbers suggest. Timings depend on hardware, interpreter and machine load, node counts are deterministic under nonbinding time limits.
