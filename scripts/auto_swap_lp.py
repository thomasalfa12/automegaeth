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

MAX_WETH_FOR_LP = web3.to_wei(0.00008, 'ether')  # Maksimal WETH untuk LP
TOTAL_ETH_TO_USE = web3.to_wei(0.00005, 'ether')  # Total ETH dipakai per loop

# ==================== ABIs ====================
with open("scripts/abi/uniswap_v2_router.json") as f:
    router_abi = json.load(f)

ERC20_ABI = [
    {"name": "symbol", "outputs": [{"type": "string"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "allowance", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}, {"type": "address"}], "stateMutability": "view", "type": "function"},
    {"name": "approve", "outputs": [{"type": "bool"}], "inputs": [{"type": "address"}, {"type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"name": "balanceOf", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
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
    except Exception:
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

def swap_weth_to_token(amount_in, token_out, nonce):
    path = [WETH_ADDRESS, token_out]
    amounts_out = router.functions.getAmountsOut(amount_in, path).call()
    amount_out_min = int(amounts_out[-1] * (1 - SLIPPAGE))
    deadline = int(time.time()) + 600

    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        amount_out_min,
        path,
        account.address,
        deadline
    ).build_transaction({
        'from': account.address,
        'gas': 300000,
        'gasPrice': web3.to_wei('0.01', 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    })

    signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"💱 Swap WETH → {get_token_symbol(token_out)}: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return nonce + 1

def get_token_balance(token):
    contract = web3.eth.contract(address=token, abi=ERC20_ABI)
    return contract.functions.balanceOf(account.address).call()

def get_token_price_in_weth(token_out, amount_token):
    # Hitung berapa WETH setara dengan amount_token token_out
    path = [token_out, WETH_ADDRESS]
    amounts = router.functions.getAmountsOut(amount_token, path).call()
    # amounts[0] = token_out, amounts[1] = WETH
    return amounts[1]

def add_liquidity(token_address, weth_amount, token_amount, nonce):
    token_symbol = get_token_symbol(token_address)
    print("📊 Detail Add Liquidity:")
    print(f" - Token Pair: {token_symbol} ({token_address})")
    print(f" - WETH Amount: {web3.from_wei(weth_amount, 'ether')} WETH")
    print(f" - Token Amount: {token_amount / (10**18):,.6f} {token_symbol}")
    print(f" - Slippage: {SLIPPAGE * 100}%")

    deadline = int(time.time()) + 600

    tx = router.functions.addLiquidity(
        WETH_ADDRESS,
        token_address,
        weth_amount,
        token_amount,
        int(weth_amount * (1 - SLIPPAGE)),
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
    print(f"✅ Add LP WETH + {token_symbol}: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return nonce + 1

# ==================== MAIN LOOP ====================
def run():
    while True:
        try:
            print(f"\n====== [ROUND] {datetime.now().isoformat()} ======")
            balance = web3.eth.get_balance(account.address)
            print(f"💰 Saldo: {web3.from_wei(balance, 'ether')} ETH")

            if balance < web3.to_wei('0.001', 'ether'):
                print("⚠️ Saldo terlalu kecil.")
                time.sleep(15)
                continue

            token_out = random.choice(TOKEN_OUTS)
            token_symbol = get_token_symbol(token_out)
            total_eth = TOTAL_ETH_TO_USE
            half_eth = total_eth // 2
            nonce = web3.eth.get_transaction_count(account.address)

            # Wrap half ETH ke WETH untuk swap
            nonce = wrap_eth(half_eth, nonce)

            # Approve WETH untuk swap
            nonce = approve_token(WETH_ADDRESS, half_eth, nonce)

            # Swap WETH ke token_out
            nonce = swap_weth_to_token(half_eth, token_out, nonce)

            print("⏳ Menunggu token settle...")
            time.sleep(4)

            # Cek saldo token hasil swap
            token_balance = get_token_balance(token_out)
            if token_balance == 0:
                print(f"⚠️ Tidak dapat token {token_symbol} setelah swap, skip loop")
                time.sleep(10)
                continue

            # Hitung berapa WETH setara dengan token_balance
            weth_needed = get_token_price_in_weth(token_out, token_balance)
            weth_for_lp = int(weth_needed * (1 + SLIPPAGE))

            if weth_for_lp > MAX_WETH_FOR_LP:
                print(f"⚠️ Token terlalu mahal, batasi WETH LP ke {web3.from_wei(MAX_WETH_FOR_LP, 'ether')} ETH")
                weth_for_lp = MAX_WETH_FOR_LP

                # Hitung ulang token_balance yang seimbang dengan WETH
                token_balance = router.functions.getAmountsOut(weth_for_lp, [WETH_ADDRESS, token_out]).call()[1]

            eth_balance = web3.eth.get_balance(account.address)
            if weth_for_lp > eth_balance:
                print(f"⚠️ ETH balance {web3.from_wei(eth_balance, 'ether')} kurang untuk LP, pakai maksimal")
                weth_for_lp = eth_balance

            # Wrap ETH untuk LP
            nonce = wrap_eth(weth_for_lp, nonce)

            # Approve token dan WETH untuk add liquidity
            nonce = approve_token(token_out, token_balance, nonce)
            nonce = approve_token(WETH_ADDRESS, weth_for_lp, nonce)

            # Add liquidity dengan nilai seimbang
            nonce = add_liquidity(token_out, weth_for_lp, token_balance, nonce)

            print("⏳ Delay 5-10 detik...\n")
            time.sleep(random.randint(5, 10))

        except Exception as e:
            print(f"❌ ERROR (main loop): {e}")
            print("🔁 Coba lagi dalam 10 detik...\n")
            time.sleep(10)


if __name__ == "__main__":
    run()
