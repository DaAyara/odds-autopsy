import hashlib
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

RPC_URL = "https://api.mainnet-beta.solana.com"

def hash_report(report):
    raw = json.dumps(report, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()

def anchor_report(report, keypair_path):
    from solders.keypair import Keypair
    from solders.transaction import Transaction
    from solders.system_program import transfer, TransferParams
    from solders.message import Message
    from solders.hash import Hash
    from solders.instruction import Instruction, AccountMeta
    from solders.pubkey import Pubkey
    import base64
    import time

    report_hash = hash_report(report)
    fixture_name = report['fixture']['name']

    with open(keypair_path, 'r') as f:
        key_data = json.load(f)
    keypair = Keypair.from_bytes(bytes(key_data))

    memo = f"odds-autopsy:{report_hash[:16]}"
    memo_bytes = memo.encode()

    MEMO_PROGRAM = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")

    blockhash_resp = requests.post(RPC_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLatestBlockhash",
        "params": [{"commitment": "confirmed"}]
    }).json()

    raw_blockhash = blockhash_resp['result']['value']['blockhash']
    blockhash = Hash.from_string(raw_blockhash)

    ix = Instruction(
        MEMO_PROGRAM,
        memo_bytes,
        [AccountMeta(keypair.pubkey(), True, False)]
    )

    msg = Message.new_with_blockhash([ix], keypair.pubkey(), blockhash)
    tx = Transaction.new_unsigned(msg)
    tx.sign([keypair], blockhash)

    tx_bytes = bytes(tx)
    encoded = base64.b64encode(tx_bytes).decode()

    send_resp = requests.post(RPC_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [encoded, {"encoding": "base64", "skipPreflight": True}]
    }).json()

    if 'result' in send_resp:
        sig = send_resp['result']
        print(f"Anchored on Solana: {sig}")
        print(f"Report: {fixture_name}")
        print(f"Hash: {report_hash[:16]}...")
        return {"signature": sig, "hash": report_hash, "memo": memo}
    else:
        print("Anchor failed:", send_resp)
        return None

if __name__ == "__main__":
    import glob
    reports_dir = os.path.join(os.path.dirname(__file__), '../../reports')
    keypair_path = os.path.join(os.path.dirname(__file__), '../../wallet.json')
    files = sorted(glob.glob(os.path.join(reports_dir, '*.json')))
    for filepath in files:
        with open(filepath, 'r') as f:
            report = json.load(f)
        print(f"Anchoring {report['fixture']['name']}...")
        result = anchor_report(report, keypair_path)
        if result:
            report['solana'] = result
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            print("Saved anchor to report file")
        print()