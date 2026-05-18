import requests
import time
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================================
#        👇 USER CONFIGURATION 👇
# ==========================================

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
ALCHEMY_URL = os.getenv("ALCHEMY_URL", "")

# Filters
MIN_BET_SIZE_USD = 0     
MAX_WALLET_NONCE = 1000     

# Filter Keywords
IGNORE_KEYWORDS = ['us-election', 'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'super-bowl']

# ==========================================
#           ⚙️ SYSTEM SETUP
# ==========================================

try:
    if "YOUR_ALCHEMY" in ALCHEMY_URL:
        w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
    else:
        w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
    
    if w3.is_connected():
        print(f"###  Alchemy Connected! Block: {w3.eth.block_number} ###")
    else:
        print("###  Alchemy Connection Failed (Check URL) ###")

except Exception as e:
    print(f"Alchemy Error: {e}")

wallet_cache = {}
seen_trade_ids = set() 
CACHE_DURATION = 3600

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_wallet_nonce(address):
    current_time = time.time()
    if address in wallet_cache:
        if current_time - wallet_cache[address]['last_checked'] < CACHE_DURATION:
            return wallet_cache[address]['nonce']
    try:
        nonce = w3.eth.get_transaction_count(address)
        wallet_cache[address] = {'nonce': nonce, 'last_checked': current_time}
        return nonce
    except:
        return 9999

def get_user_stats(address):
    stats = {"pnl": "$0.00", "volume": "$0.00"}
    try:
        url = f"https://data-api.polymarket.com/v1/leaderboard?category=OVERALL&timePeriod=ALL&limit=1&user={address}"
        resp = requests.get(url, headers=HEADERS, timeout=2).json()
        
        if resp and len(resp) > 0:
            data = resp[0]
            pnl = float(data.get('pnl', 0))
            stats['pnl'] = f"+${pnl:,.2f}" if pnl >= 0 else f"-${abs(pnl):,.2f}"
            vol = float(data.get('volume', 0))
            stats['volume'] = f"${vol:,.0f}"
        return stats
    except:
        return stats

def get_market_details(market_slug, event_slug):
    details = {
        "candidate": "", 
        "event_title": market_slug.replace("-", " ").title(),
        "image": "https://polymarket.com/favicon.ico"
    }
    try:
        # 1. Ask Gamma API for specific market details
        url = f"https://gamma-api.polymarket.com/markets?slug={market_slug}"
        resp = requests.get(url, headers=HEADERS, timeout=2).json()
        
        if resp and isinstance(resp, list) and len(resp) > 0:
            data = resp[0]
            # Candidate Logic
            if data.get('groupItemTitle'):      
                details['candidate'] = data.get('groupItemTitle')
            elif data.get('question'):          
                details['candidate'] = data.get('question')
            # Image Logic
            if data.get('image'):
                details['image'] = data.get('image')
            elif data.get('icon'):
                details['image'] = data.get('icon')

        # 2. Ask Event API for the "Main Topic"
        evt_url = f"https://gamma-api.polymarket.com/events?slug={event_slug}"
        evt_resp = requests.get(evt_url, headers=HEADERS).json()
        
        if evt_resp:
            event_data = evt_resp[0]
            details['event_title'] = event_data.get('title', details['event_title'])
            if details['image'] == "https://polymarket.com/favicon.ico":
                details['image'] = event_data.get('image', details['image'])
        
        # Failsafe
        if not details['candidate']:
            details['candidate'] = details['event_title']
    except:
        pass
    return details

def send_discord_alert(data):
    if not DISCORD_WEBHOOK_URL or "YOUR_DISCORD" in DISCORD_WEBHOOK_URL: return
    
    try:
        share_count = data['size_usd'] / data['price']
    except:
        share_count = 0
    
    price_cents = data['price'] * 100
    color = 5763719 if data['side'] == "BUY" else 15548997
    
    embed = {
        "author": {
            "name": "🍃 Low Activity Wallet",
        },
        "title": data['candidate_name'], 
        "url": data['link'],
        "description": f"Event: **[{data['event_name']}]({data['link']})**\nOutcome: **{data['outcome']}**",
        "color": color,
        "thumbnail": {"url": data['image_url']},
        "image": {"url": data['image_url']},
        "fields": [
            # --- ROW 1 ---
            {
                "name": "Trader",
                "value": f"[{data['wallet'][:6]}...](https://polygonscan.com/address/{data['wallet']})",
                "inline": True
            },
            {
                "name": "Side",
                "value": f"**{data['side']}**",
                "inline": True
            },
            {
                "name": "Trade",
                "value": f"{share_count:,.0f} shares @ {price_cents:.1f}¢",
                "inline": True
            },
            
            # --- ROW 2 ---
            {
                "name": "Notional",
                "value": f"${data['size_usd']:,.0f}",
                "inline": True
            },
            {
                "name": "Tx Count",   # <--- NEW FIELD ADDED HERE
                "value": str(data['nonce']),
                "inline": True
            },
            {
                "name": "Lifetime PnL", 
                "value": data['stats']['pnl'],
                "inline": True
            },
            # Note: I removed Volume to keep the layout clean (3x2 grid), 
            # but you can add it back if you prefer 4 items in a row.
        ],
        "footer": {"text": f"Polymarket Watcher • {time.strftime('%Y-%m-%d, %H:%M:%S')}"}
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"username": "Polymarket Watch", "embeds": [embed]})
        print(f" Alert Sent: {data['candidate_name']}")
    except Exception as e:
        print(f"Discord Error: {e}")

def check_market():
    try:
        url = "https://data-api.polymarket.com/trades?limit=27"
        response = requests.get(url, headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            trades = response.json()
            for trade in reversed(trades): 
                
                trade_id = f"{trade.get('matchId')}-{trade.get('timestamp')}"
                if trade_id in seen_trade_ids: continue
                seen_trade_ids.add(trade_id)
                
                price = float(trade.get('price', 0))
                size = float(trade.get('size', 0))
                size_usd = size * price
                
                if size_usd < MIN_BET_SIZE_USD: continue
                
                # Nuclear Filter
                check_text = (
                    str(trade.get('marketSlug', '')) + 
                    str(trade.get('slug', '')) + 
                    str(trade.get('eventSlug', '')) + 
                    str(trade.get('asset', ''))
                ).lower()
                
                if any(k in check_text for k in IGNORE_KEYWORDS): 
                    continue
                
                user_address = trade.get('taker') or trade.get('proxyWallet')
                if not user_address: continue
                
                nonce = get_wallet_nonce(user_address)
                
                if nonce <= MAX_WALLET_NONCE:
                    event_slug = trade.get('eventSlug', '')
                    market_slug = trade.get('marketSlug') or trade.get('slug', '')
                    final_slug = event_slug if event_slug else market_slug
                    
                    details = get_market_details(market_slug, event_slug)
                    user_stats = get_user_stats(user_address)

                    alert_data = {
                        "wallet": user_address,
                        "size_usd": size_usd,
                        "price": price,
                        "side": trade.get('side', 'BUY').upper(),
                        "outcome": trade.get('outcome', 'YES'),
                        "nonce": nonce,
                        "stats": user_stats,
                        "candidate_name": details['candidate'], 
                        "event_name": details['event_title'],   
                        "link": f"https://polymarket.com/event/{final_slug}", 
                        "image_url": details['image']
                    }
                    print(f"⚡ MATCH: {alert_data['side']} {alert_data['outcome']} on {details['candidate']}")
                    send_discord_alert(alert_data)
        else:
            print(f" API Status: {response.status_code}")
            
    except Exception as e:
        print(f"Loop Error: {e}")

if __name__ == "__main__":
    print("###  Bot Starting (With Nonce) ###")
    print("### Waiting for trades... ###")
    while True:
        try:
            check_market()
            time.sleep(2) # Normal wait
        except Exception as e:
            print(f" Internet/API Error: {e}")
            print(" Waiting 10 seconds before trying again...")
            time.sleep(10) # Long wait when broken