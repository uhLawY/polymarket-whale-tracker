# Polymarket Hidden Whale Tracker
An automated Python script that streams live trades from Polymarket and uses Web3/Alchemy RPC nodes to flag low-nonce (freshly made) whale wallets.

## Prerequisites
- pip install requests web3 python-dotenv

## Setup
Create a `.env` file containing your `DISCORD_WEBHOOK_URL` and `ALCHEMY_URL`. Run `python monitor2.py`.