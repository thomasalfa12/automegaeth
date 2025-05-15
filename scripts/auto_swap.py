import os
import time
import json
import random
from datetime import datetime
from decimal import Decimal, getcontext
from dotenv import load_dotenv
from web3 import Web3
from scripts.token_outs import TOKEN_OUTS


# ==================== SETUP ====================
getcontext().prec = 18
load_dotenv()

def require_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"❌ Missing env var: {key}")
    return value

# Load ENV variables
PRIVATE_KEY = require_env("PRIVATE_KEY")
RPC_URL = require_env("RPC_URL")
CHAIN_ID = int(require_env("CHAIN_ID"))
ROUTER_ADDRESS = Web3.to_checksum_address(require_env("ROUTER_ADDRESS"))
WETH_ADDRESS = Web3.to_checksum_address("0x776401b9bc8aae31a685731b7147d4445fd9fb19")

SLIPPAGE = 0.1  # 10%

web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

# Load Router ABI
with open("scripts/abi/uniswap_v2_router.json") as f:
    router_abi = json.load(f)

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)
# ==================== ABI WETH + ERC20 ====================
ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
]

WETH_ABI = ERC20_ABI + [
    {"constant": False, "inputs": [], "name": "deposit", "outputs": [], "payable": True,
     "stateMutability": "payable", "type": "function"}
]

weth_contract = web3.eth.contract(address=WETH_ADDRESS, abi=WETH_ABI)

# ==================== HELPERS ====================
def get_token_symbol(token_address: str) -> str:
    try:
        token = web3.eth.contract(address=token_address, abi=ERC20_ABI)
        return token.functions.symbol().call()
    except Exception:
        return "Unknown"

# ==================== LOGIC ====================
def wrap_eth(amount: int, nonce: int) -> int:
    try:
        tx = weth_contract.functions.deposit().build_transaction({
            'from': account.address,
            'value': amount,
            'gas': 100000,
            'gasPrice': web3.to_wei('0.01', 'gwei'),
            'nonce': nonce,
            'chainId': CHAIN_ID
        })
        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Wrap ETH ke WETH: https://web3.okx.com/explorer/megaeth-testnet/tx/0x{tx_hash.hex()}")
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return nonce + 1
    except Exception as e:
        print(f"❌ Gagal wrap ETH: {e}")
        return nonce

def approve_weth(amount: int, nonce: int) -> int:
    try:
        allowance = weth_contract.functions.allowance(account.address, ROUTER_ADDRESS).call()
        if allowance >= amount:
            print("ℹ️ WETH sudah di-approve.")
            return nonce

        tx = weth_contract.functions.approve(ROUTER_ADDRESS, amount).build_transaction({
            'from': account.address,
            'gas': 80000,
            'gasPrice': web3.to_wei('0.01', 'gwei'),
            'nonce': nonce,
            'chainId': CHAIN_ID
        })
        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Approve WETH: https://web3.okx.com/explorer/megaeth-testnet/tx/0x{tx_hash.hex()}")
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return nonce + 1
    except Exception as e:
        print(f"❌ Approve gagal: {e}")
        return nonce

def swap_weth_to_token(token_out: str, amount_in: int, nonce: int):
    try:
        path = [WETH_ADDRESS, token_out]
        deadline = int(time.time()) + 600

        try:
            amounts = router.functions.getAmountsOut(amount_in, path).call()
        except Exception as e:
            print(f"⚠️ Gagal mendapatkan amountOut: {e}")
            return

        amount_out_min = int(Decimal(amounts[1]) * Decimal(1 - SLIPPAGE))
        symbol = get_token_symbol(token_out)

        print(f"💱 Swap {web3.from_wei(amount_in, 'ether')} WETH → minimal {web3.from_wei(amount_out_min, 'ether')} {symbol}")

        if amount_out_min < 1:
            print("⚠️ amountOut terlalu kecil. Skip.")
            return

        tx = router.functions.swapExactTokensForTokens(
            amount_in, amount_out_min, path, account.address, deadline
        ).build_transaction({
            'from': account.address,
            'gas': 240000,
            'gasPrice': web3.to_wei('0.01', 'gwei'),
            'nonce': nonce,
            'chainId': CHAIN_ID
        })
        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Swap berhasil! https://web3.okx.com/explorer/megaeth-testnet/tx/0x{tx_hash.hex()}")
    except Exception as e:
        print(f"❌ Gagal swap: {e}")
        if "execution reverted" in str(e):
            print("⚠️ Revert: Cek slippage atau token tidak ada pool.")

# ==================== MAIN LOOP ====================
def run_loop():
    while True:
        try:
            print("\n================== [NEW ROUND] ==================")
            print(f"[{datetime.now().isoformat()}] Mulai loop oleh: {account.address}")

            balance = web3.eth.get_balance(account.address)
            print(f"Saldo ETH: {web3.from_wei(balance, 'ether')} ETH")

            if balance < web3.to_wei('0.001', 'ether'):
                print("⚠️ Saldo terlalu rendah.")
                time.sleep(15)
                continue

            token_out = random.choice(TOKEN_OUTS)
            symbol = get_token_symbol(token_out)

            amount_in = web3.to_wei(random.uniform(0.000025, 0.00005), 'ether')
            nonce = web3.eth.get_transaction_count(account.address)

            nonce = wrap_eth(amount_in, nonce)
            nonce = approve_weth(amount_in, nonce)
            swap_weth_to_token(token_out, amount_in, nonce)

            sleep_time = random.randint(5, 10)
            print(f"⏳ Menunggu {sleep_time} detik...\n")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ ERROR (main loop): {e}")
            print("🔁 Retry dalam 10 detik...\n")
            time.sleep(10)

if __name__ == "__main__":
    run_loop()
