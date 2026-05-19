# Polymarket Whale Tracker

A Python-based automation tool that monitors whale activity on Polymarket in real time and sends actionable alerts directly to Discord.

Built to track high-volume wallet activity, detect newly created wallets, and identify unusual trading behavior across prediction markets using on-chain and API-driven data sources.

---

## Features

- Real-time whale wallet monitoring
- Polymarket API integration
- Discord webhook alerting
- Transaction filtering & duplicate prevention
- Environment variable secret management
- Lightweight automation workflow
- Modular and extendable architecture

---

## Tech Stack

- Python
- Polymarket API
- Discord Webhooks
- Web3 / RPC Endpoints
- dotenv (`python-dotenv`)

---

## How It Works

1. Fetches market and wallet activity from Polymarket APIs
2. Monitors newly active wallets and large transactions
3. Applies filtering and caching logic to reduce duplicate alerts
4. Sends formatted whale activity notifications to Discord channels

---

## Example Alert

```bash
🐋 Whale Alert Detected

Wallet: 0x1234...abcd
Market: US Election 2028
Position: YES
Volume: $42,500
Timestamp: 2026-05-19 13:42 UTC
```
<img width="671" height="607" alt="image" src="https://github.com/user-attachments/assets/0f983f16-8f06-4062-b380-dd13af1ef772" />

---

## Project Structure

```bash
polymarket-whale-tracker/
│
├── main.py
├── tracker.py
├── alerts.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/uhLawY/polymarket-whale-tracker.git
cd polymarket-whale-tracker
```

Install dependencies:

```bash
pip install -r requests web3 dotenv
```

Create a `.env` file:

```env
DISCORD_WEBHOOK_URL=Your Discord Webhook 
ALCHEMY_URL=Your Alchemy Polygon Api Url
```

Run the tracker:

```bash
python monitor2.py
```

---

## Security Considerations

Sensitive credentials are stored using environment variables via `python-dotenv` to prevent accidental secret exposure in source code.

Never commit:
- `.env`
- private keys
- webhook URLs
- API credentials

Several crypto-related GitHub projects have recently been found distributing malicious packages targeting `.env` files and wallet credentials, making secure secret management especially important for blockchain tooling. :contentReference[oaicite:1]{index=1}

---

## Future Improvements

- Telegram alert integration
- Whale scoring system
- Historical wallet analytics
- Web dashboard
- Trade visualization charts
- Multi-market tracking
- SQLite/PostgreSQL logging backend

---

## Disclaimer

This project is intended for educational and research purposes only.

It is not financial advice and should not be used as the sole basis for trading decisions.

---

## Author

Law Jun Feng

GitHub: https://github.com/uhLawY
LinkedIn: https://www.linkedin.com/in/law-jun-feng-8a714022a/
