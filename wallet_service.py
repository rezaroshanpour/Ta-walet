# services/wallet_service.py

from eth_account import Account
from web3 import Web3
from pytoniq import LiteClient
import asyncio

CLOUDFLARE_URL = "https://cloudflare-eth.com"
w3 = Web3(Web3.HTTPProvider(CLOUDFLARE_URL))
Account.enable_unaudited_hdwallet_features()

def create_new_wallet():
    return Account.create_with_mnemonic()

def get_address_from_mnemonic(mnemonic):
    return Account.from_mnemonic(mnemonic).address

def get_eth_balance(address):
    try:
        return w3.from_wei(w3.eth.get_balance(address), 'ether')
    except Exception:
        return 0

async def get_ton_balance_async(address):
    try:
        client = LiteClient.from_mainnet_config()
        await client.connect()
        balance_nanoton = await client.get_balance(address)
        await client.close()
        return balance_nanoton / 1_000_000_000
    except Exception:
        return 0

def get_ton_balance(address):
    return asyncio.run(get_ton_balance_async(address))