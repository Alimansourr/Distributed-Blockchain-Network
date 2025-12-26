import requests
import time
import csv
import os

# ---------------- CONFIG FOR THIS RUN ----------------
BASE_URL = "http://127.0.0.1:5000"  # node to test through
RECEIVER_ID = 1                     # send from node 0 to node 1
AMOUNT = 1                          # 1 NDC per transaction
N_TX = 20                           # number of transactions to send

# Describe this experiment (will be saved in CSV)
EXPERIMENT_NAME = "2nodes_cap1_diff4_run1"
N_NODES = 2                         # how many nodes in the network
CAPACITY = None                     # will be overwritten from /api/get_metrics
DIFFICULTY = None                   # will be overwritten from /api/get_metrics

RESULTS_FILE = "results.csv"        # CSV file in src/ (or wherever you prefer)
# -----------------------------------------------------


def main():
    global CAPACITY, DIFFICULTY

    total_http_time = 0.0
    total_mining_time = 0.0
    success = 0

    print(f"Starting experiment: {N_TX} tx from node 0 -> node {RECEIVER_ID}")
    for i in range(N_TX):
        data = {"receiver": RECEIVER_ID, "amount": AMOUNT}
        t0 = time.time()
        try:
            resp = requests.post(BASE_URL + "/api/create_transaction", data=data)
        except Exception as e:
            print(f"Request failed at tx {i}: {e}")
            break

        dt = time.time() - t0

        try:
            js = resp.json()
        except Exception:
            print(f"Non-JSON response at tx {i}, status={resp.status_code}")
            break

        msg = js.get("message", "")
        mining_time = js.get("mining_time", 0.0)

        print(f"TX {i+1}/{N_TX}: status={resp.status_code}, msg={msg}, mining_time={mining_time:.4f}s")

        if resp.status_code == 200:
            total_http_time += dt
            total_mining_time += mining_time
            success += 1
        else:
            print("Stopping due to error.")
            break

    print("\n=== Raw results ===")
    print(f"Successful transactions: {success}/{N_TX}")
    print(f"Total HTTP time (s): {total_http_time:.4f}")
    if total_http_time > 0:
        throughput = success / total_http_time
        print(f"Throughput (tx/s): {throughput:.4f}")
    else:
        throughput = 0.0
        print("Throughput: undefined (no successful tx)")

    # get blockchain metrics from the node
    try:
        metrics = requests.get(BASE_URL + "/api/get_metrics").json()
        num_blocks = metrics["num_blocks"]
        DIFFICULTY = metrics["difficulty"]
        CAPACITY = metrics["capacity"]
        effective_blocks = max(1, num_blocks - 1)  # ignore genesis
        avg_block_time = total_mining_time / effective_blocks

        print("\n=== Blockchain metrics ===")
        print(f"num_blocks (including genesis): {num_blocks}")
        print(f"difficulty: {DIFFICULTY}")
        print(f"capacity: {CAPACITY}")
        print(f"Average mining time per block (s): {avg_block_time:.4f}")
    except Exception as e:
        print(f"Error getting metrics: {e}")
        num_blocks = 0
        avg_block_time = 0.0

    # -------- SAVE RESULTS TO CSV --------
    save_results(
        EXPERIMENT_NAME,
        N_NODES,
        CAPACITY,
        DIFFICULTY,
        N_TX,
        success,
        total_http_time,
        throughput,
        num_blocks,
        avg_block_time
    )


def save_results(
    experiment_name,
    n_nodes,
    capacity,
    difficulty,
    n_tx,
    success,
    total_http_time,
    throughput,
    num_blocks,
    avg_block_time
):
    file_exists = os.path.isfile(RESULTS_FILE)

    with open(RESULTS_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)

        # write header once
        if not file_exists:
            writer.writerow([
                "experiment_name",
                "n_nodes",
                "capacity",
                "difficulty",
                "n_tx",
                "success_tx",
                "total_http_time",
                "throughput",
                "num_blocks",
                "avg_block_time"
            ])

        writer.writerow([
            experiment_name,
            n_nodes,
            capacity,
            difficulty,
            n_tx,
            success,
            total_http_time,
            throughput,
            num_blocks,
            avg_block_time
        ])

    print(f"\nResults saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
