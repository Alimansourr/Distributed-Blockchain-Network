import csv
from collections import defaultdict

import matplotlib.pyplot as plt


RESULTS_FILE = "results.csv"


def load_results():
    rows = []
    with open(RESULTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # convert numeric fields from string to float/int
            row["n_nodes"] = int(row["n_nodes"])
            row["capacity"] = int(row["capacity"])
            row["difficulty"] = int(row["difficulty"])
            row["n_tx"] = int(row["n_tx"])
            row["success_tx"] = int(row["success_tx"])
            row["total_http_time"] = float(row["total_http_time"])
            row["throughput"] = float(row["throughput"])
            row["num_blocks"] = int(row["num_blocks"])
            row["avg_block_time"] = float(row["avg_block_time"])
            rows.append(row)
    return rows


def plot_throughput_vs_capacity(rows):
    # group by capacity, average throughput
    by_cap = defaultdict(list)
    for r in rows:
        by_cap[r["capacity"]].append(r["throughput"])

    caps = sorted(by_cap.keys())
    thr = [sum(by_cap[c]) / len(by_cap[c]) for c in caps]

    plt.figure()
    plt.plot(caps, thr, marker="o")
    plt.xlabel("Block capacity (transactions per block)")
    plt.ylabel("Throughput (tx/s)")
    plt.title("Throughput vs Block Capacity")
    plt.grid(True)
    plt.show()


def plot_block_time_vs_difficulty(rows):
    by_diff = defaultdict(list)
    for r in rows:
        by_diff[r["difficulty"]].append(r["avg_block_time"])

    diffs = sorted(by_diff.keys())
    times = [sum(by_diff[d]) / len(by_diff[d]) for d in diffs]

    plt.figure()
    plt.plot(diffs, times, marker="o")
    plt.xlabel("Difficulty (leading zeros)")
    plt.ylabel("Average block time (s)")
    plt.title("Average Block Time vs Difficulty")
    plt.grid(True)
    plt.show()


def plot_throughput_vs_nodes(rows):
    by_nodes = defaultdict(list)
    for r in rows:
        by_nodes[r["n_nodes"]].append(r["throughput"])

    ns = sorted(by_nodes.keys())
    thr = [sum(by_nodes[n]) / len(by_nodes[n]) for n in ns]

    plt.figure()
    plt.plot(ns, thr, marker="o")
    plt.xlabel("Number of nodes")
    plt.ylabel("Throughput (tx/s)")
    plt.title("Throughput vs Number of Nodes")
    plt.grid(True)
    plt.show()


def main():
    rows = load_results()
    print(f"Loaded {len(rows)} experiments from {RESULTS_FILE}")

    # Call whichever plots you have data for
    plot_throughput_vs_capacity(rows)
    plot_block_time_vs_difficulty(rows)
    plot_throughput_vs_nodes(rows)


if __name__ == "__main__":
    main()
