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

PRIVATE_KEY = require_env("PRIVATE_KEY")
RPC_URL = require_env("RPC_URL")
CHAIN_ID = int(require_env("CHAIN_ID"))
ROUTER_ADDRESS = Web3.to_checksum_address(require_env("ROUTER_ADDRESS"))
WETH_ADDRESS = Web3.to_checksum_address("0x776401b9bc8aae31a685731b7147d4445fd9fb19")

SLIPPAGE = 0.1  # 10%

web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

# ==================== ABIs ====================
with open("scripts/abi/uniswap_v2_router.json") as f:
    router_abi = json.load(f)

ERC20_ABI = [
    {"name": "symbol", "outputs": [{"type": "string"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "allowance", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}, {"type": "address"}], "stateMutability": "view", "type": "function"},
    {"name": "approve", "outputs": [{"type": "bool"}], "inputs": [{"type": "address"}, {"type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
]

WETH_ABI = ERC20_ABI + [
    {"name": "deposit", "outputs": [], "inputs": [], "stateMutability": "payable", "type": "function"},
]

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)
weth_contract = web3.eth.contract(address=WETH_ADDRESS, abi=WETH_ABI)

# ==================== HELPERS ====================
def get_token_symbol(token_addr):
    try:
        contract = web3.eth.contract(address=token_addr, abi=ERC20_ABI)
        return contract.functions.symbol().call()
    except:
        return "UNKNOWN"

def approve_token(token, amount, nonce):
    contract = web3.eth.contract(address=token, abi=ERC20_ABI)
    allowance = contract.functions.allowance(account.address, ROUTER_ADDRESS).call()
    if allowance >= amount:
        print(f"✅ Sudah approve token {get_token_symbol(token)}")
        return nonce

    tx = contract.functions.approve(ROUTER_ADDRESS, amount).build_transaction({
        'from': account.address,
        'gas': 80000,
        'gasPrice': web3.to_wei('0.01', 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    })
    signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"🔑 Approve {get_token_symbol(token)}: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return nonce + 1

def wrap_eth(amount, nonce):
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
    print(f"💧 Wrap ETH: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return nonce + 1

# ==================== MAIN LP ====================
def add_liquidity(token_address, target_eth_value_wei, nonce):
    try:
        path = [WETH_ADDRESS, token_address]
        amounts_out = router.functions.getAmountsOut(target_eth_value_wei, path).call()
        token_amount = amounts_out[1]
        token_symbol = get_token_symbol(token_address)

        approve_amount_token = int(token_amount * 1.10)

        print("📊 Detail Add Liquidity:")
        print(f" - Token Pair: {token_symbol} ({token_address})")
        print(f" - Target ETH: {web3.from_wei(target_eth_value_wei, 'ether')} ETH")
        print(f" - Required {token_symbol}: {token_amount / (10**18):,.6f}")
        print(f" - Approval {token_symbol} (+10%): {approve_amount_token / (10**18):,.6f}")
        print(f" - Slippage: {SLIPPAGE * 100}%")

        nonce = wrap_eth(target_eth_value_wei, nonce)
        nonce = approve_token(token_address, approve_amount_token, nonce)
        nonce = approve_token(WETH_ADDRESS, target_eth_value_wei, nonce)

        deadline = int(time.time()) + 600
        tx = router.functions.addLiquidity(
            WETH_ADDRESS,
            token_address,
            target_eth_value_wei,
            token_amount,
            int(target_eth_value_wei * (1 - SLIPPAGE)),
            int(token_amount * (1 - SLIPPAGE)),
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'gas': 400000,
            'gasPrice': web3.to_wei('0.01', 'gwei'),
            'nonce': nonce,
            'chainId': CHAIN_ID
        })
        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Add Liquidity WETH + {token_symbol}: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    except Exception as e:
        print(f"❌ Gagal add LP: {e}")

# ==================== LOOP ====================
def run():
    while True:
        try:
            print(f"\n====== [START ROUND] {datetime.now().isoformat()} ======")
            balance = web3.eth.get_balance(account.address)
            print(f"Saldo: {web3.from_wei(balance, 'ether')} ETH")

            if balance < web3.to_wei('0.001', 'ether'):
                print("⚠️ Saldo terlalu kecil.")
                time.sleep(15)
                continue

            token = random.choice(TOKEN_OUTS)
            target_eth_value_wei = web3.to_wei(0.000025, 'ether')
            nonce = web3.eth.get_transaction_count(account.address)

            add_liquidity(token, target_eth_value_wei, nonce)


            sleep_time = random.randint(5, 10)
            print(f"⏳ Tidur {sleep_time} detik...\n")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ ERROR (main loop): {e}")
            print("🔁 Coba lagi dalam 10 detik...\n")
            time.sleep(10)

if __name__ == "__main__":
    run()
