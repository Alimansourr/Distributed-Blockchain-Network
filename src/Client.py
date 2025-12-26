import requests
import socket
import pickle
import config
import subprocess
from argparse import ArgumentParser

# --- IP detection (same idea as before) ---

def ip_address():
    # Only used if LOCAL = False (Linux case)
    result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'inet ' in line and '127.0.0.1' not in line:
            ip_address = line.split()[1].split('/')[0]
            if ip_address.startswith('192.168'):
                return ip_address
    return None

if config.LOCAL:
    IPAddr = '127.0.0.1'
else:
    hostname = socket.gethostname()
    IPAddr = ip_address()


def print_menu():
    print("\n=== MiniChain Client ===")
    print("1) New transaction")
    print("2) View last block transactions")
    print("3) Show balance")
    print("4) Help")
    print("0) Exit")


def new_transaction(base_url):
    try:
        receiver = input("Receiver ID: ").strip()
        amount = input("Amount: ").strip()

        if not receiver.isdigit() or not amount.isdigit():
            print("Receiver and amount must be integers.")
            return

        receiver = int(receiver)
        amount = int(amount)

        confirm = input(f"Confirm transaction {amount} -> {receiver}? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Transaction aborted.")
            return

        resp = requests.post(
            base_url + "/api/create_transaction",
            data={"receiver": receiver, "amount": amount}
        )

        if resp.status_code == 200:
            data = resp.json()
            print(f"\n{data.get('message', '')}")
            print(f"New balance: {data.get('balance', 'N/A')} NDC")
            print(f"Mining time: {data.get('mining_time', 0):.4f} s")
        else:
            try:
                data = resp.json()
                print(f"\n{data.get('message', 'Error')}")
                print(f"Balance: {data.get('balance', 'N/A')} NDC")
            except Exception:
                print("\nError creating transaction.")
    except requests.exceptions.RequestException:
        print("\nNode is not active, try again later.")


def view_last_transactions(base_url):
    try:
        resp = requests.get(base_url + "/api/get_transactions")
        if resp.status_code != 200:
            print("\nError getting transactions.")
            return

        data = pickle.loads(resp.content)

        print("\nTransactions of last valid block of MiniChain's blockchain:")
        print("-----------------------------------------------------------")
        if not data:
            print("No transactions in last block.")
            return

        print(f"{'sender_id':>10} {'receiver_id':>12} {'amount':>8} {'total':>8} {'change':>8}")
        print("-" * 50)
        for row in data:
            s_id, r_id, amount, total, change = row
            print(f"{s_id:>10} {r_id:>12} {amount:>8} {total:>8} {change:>8}")
    except requests.exceptions.RequestException:
        print("\nNode is not active, try again later.")


def show_balance(base_url):
    try:
        resp = requests.get(base_url + "/api/get_balance")
        if resp.status_code != 200:
            print("\nError getting balance.")
            return

        data = resp.json()
        balance = data.get('balance', 'N/A')
        print(f"\nCurrent balance: {balance} NDC")
    except requests.exceptions.RequestException:
        print("\nNode is not active, try again later.")


def show_help():
    print("\nHelp")
    print("----")
    print("1) New transaction: send NDC to another node by ID (receiver_id, amount).")
    print("2) View last block transactions: shows all transactions in the last confirmed block.")
    print("3) Show balance: prints your current wallet balance.")
    print("0) Exit: close the client.")


def main():
    parser = ArgumentParser(description='CLI client of MiniChain.')
    parser.add_argument('-p', type=int, help='port of the node to connect to', required=True)
    args = parser.parse_args()

    port = args.p
    base_url = f"http://{IPAddr}:{port}"

    print(f"Connecting to node at {base_url} ...")

    while True:
        print_menu()
        choice = input("Select option: ").strip()

        if choice == '1':
            new_transaction(base_url)
        elif choice == '2':
            view_last_transactions(base_url)
        elif choice == '3':
            show_balance(base_url)
        elif choice == '4':
            show_help()
        elif choice == '0':
            print("Exiting client.")
            break
        else:
            print("Invalid option. Please choose 0–4.")


if __name__ == "__main__":
    main()
