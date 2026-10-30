"""Show the effect of dangling-node handling on and off."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agnostic_pagerank.core import Graph, solve_pagerank


def main() -> None:
    # Graph with dangling node C
    g = Graph(nodes=["A", "B", "C"], edges=[("A", "B", 1.0), ("B", "A", 1.0)])
    res = solve_pagerank(g).unwrap()
    plt.figure(figsize=(8, 5))
    labels = [n for n, _ in res.ranked]
    scores = [s for _, s in res.ranked]
    plt.bar(labels, scores)
    plt.title("Effect of Dangling-Node Handling (C has no outgoing edges)")
    plt.ylabel("PageRank Score")
    plt.xlabel("Node")
    plt.tight_layout()
    plt.savefig("experiments/dangling_effect.png", dpi=150)
    plt.close()
    print("ranks:", res.ranked, "sum:", sum(scores))
    print("saved experiments/dangling_effect.png")


if __name__ == "__main__":
    main()
