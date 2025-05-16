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
FACTORY_ADDRESS = Web3.to_checksum_address(require_env("FACTORY_ADDRESS"))
WETH_ADDRESS = Web3.to_checksum_address("0x776401b9bc8aae31a685731b7147d4445fd9fb19")

SLIPPAGE = 0.1

web3 = Web3(Web3.HTTPProvider(RPC_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

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

factory_abi = [{
    "name": "getPair",
    "type": "function",
    "inputs": [
        { "name": "tokenA", "type": "address" },
        { "name": "tokenB", "type": "address" }
    ],
    "outputs": [
        { "name": "pair", "type": "address" }
    ],
    "stateMutability": "view"
}]

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)
factory = web3.eth.contract(address=FACTORY_ADDRESS, abi=factory_abi)
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

def get_lp_token_address(token_a, token_b):
    # Urutkan agar konsisten sesuai UniswapV2 getPair
    if token_a.lower() > token_b.lower():
        token_a, token_b = token_b, token_a
    return factory.functions.getPair(token_a, token_b).call()

# ==================== SWAP & LP ====================
def swap_and_add_liquidity(token_address, eth_amount, nonce):
    path = [WETH_ADDRESS, token_address]
    symbol = get_token_symbol(token_address)

    nonce = wrap_eth(eth_amount, nonce)
    nonce = approve_token(WETH_ADDRESS, eth_amount, nonce)

    try:
        amount_out = router.functions.getAmountsOut(eth_amount, path).call()[1]
    except Exception as e:
        print(f"❌ Gagal getAmountsOut: {e}")
        return nonce

    min_out = int(amount_out * (1 - SLIPPAGE))

    tx = router.functions.swapExactTokensForTokens(
        eth_amount, min_out, path, account.address, int(time.time()) + 600
    ).build_transaction({
        'from': account.address,
        'gas': 240000,
        'gasPrice': web3.to_wei('0.01', 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    })
    signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"💱 Swap WETH → {symbol}: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    nonce += 1

    nonce = approve_token(token_address, amount_out, nonce)

    tx = router.functions.addLiquidity(
        WETH_ADDRESS,
        token_address,
        eth_amount,
        amount_out,
        int(eth_amount * (1 - SLIPPAGE)),
        int(amount_out * (1 - SLIPPAGE)),
        account.address,
        int(time.time()) + 600
    ).build_transaction({
        'from': account.address,
        'gas': 400000,
        'gasPrice': web3.to_wei('0.01', 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    })
    signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Add LP WETH + {symbol}: https://web3.okx.com/explorer/megaeth-testnet/tx/{tx_hash.hex()}")
    web3.eth.wait_for_transaction_receipt(tx_hash)

    return nonce + 1

def sort_tokens(token_a, token_b):
    return (token_a, token_b) if token_a.lower() < token_b.lower() else (token_b, token_a)

def get_pair_address(tokenA, tokenB):
    factory = web3.eth.contract(address=FACTORY_ADDRESS, abi=factory_abi)
    return factory.functions.getPair(tokenA, tokenB).call()

def get_lp_token(pair_address):
    return web3.eth.contract(address=pair_address, abi=ERC20_ABI)


#============= REMOVE LP ====================#
def remove_lp(token0, token1, nonce):
    # Cek pair address
    pair_address = get_pair_address(token0, token1)
    lp_token = get_lp_token(pair_address)

    # Ambil balance LP yang tersedia
    lp_balance = lp_token.functions.balanceOf(account.address).call()
    if lp_balance == 0:
        print(f"❌ Tidak ada LP untuk pair {token0[:6]}... / {token1[:6]}...")
        return nonce

    # Hitung 30% dari total LP
    remove_amount = int(lp_balance * 0.3)
    print(f"🔥 Menghapus {remove_amount / (10 ** 18):.6f} LP ({int((remove_amount/lp_balance)*100)}%) dari {lp_balance / (10 ** 18):.6f} total LP")

    # Approve router untuk LP
    tx = lp_token.functions.approve(ROUTER_ADDRESS, remove_amount).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': web3.to_wei('0.02', 'gwei'),
    })
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"🔑 Approve LP: {EXPLORER_TX}{web3.to_hex(tx_hash)}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    nonce += 1

    # Remove liquidity
    tx = router.functions.removeLiquidityETH(
        token0,
        remove_amount,
        0,
        0,
        account.address,
        int(time.time()) + 1000
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': web3.to_wei('0.01', 'gwei'),
    })
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"✅ Remove LP: {EXPLORER_TX}{web3.to_hex(tx_hash)}")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    nonce += 1

    return nonce
# ==================== LOOP ====================
lp_counter = 0
target_remove_interval = random.randint(2, 5)

def run():
    global lp_counter, target_remove_interval
    while True:
        try:
            print(f"\n====== [LOOP] {datetime.now().isoformat()} ======")
            balance = web3.eth.get_balance(account.address)
            print(f"💰 Saldo: {web3.from_wei(balance, 'ether')} ETH")

            if balance < web3.to_wei('0.001', 'ether'):
                print("⚠️ Saldo terlalu kecil.")
                time.sleep(10)
                continue

            token = random.choice(TOKEN_OUTS)
            eth_amount = web3.to_wei(0.00003, 'ether')
            nonce = web3.eth.get_transaction_count(account.address)

            swap_and_add_liquidity(token, eth_amount, nonce)
            lp_counter += 1

            if lp_counter >= target_remove_interval:
                print(f"🔁 Target {target_remove_interval} LP reached, removing LP...")
                nonce = web3.eth.get_transaction_count(account.address)
                token0, token1 = sort_tokens(WETH_ADDRESS, token)
                nonce = remove_lp(token0, token1, nonce)
                lp_counter = 0
                target_remove_interval = random.randint(3, 5)


            sleep_time = random.randint(5, 10)
            print(f"⏳ Tidur {sleep_time} detik...\n")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run()
