import requests
import datetime

# ===== 配置 =====
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
# Bybit ETH 永续（USDT）
BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=linear&symbol=ETHUSDT"


def get_eth_price():
    r = requests.get(BYBIT_URL)
    data = r.json()

    price = data["result"]["list"][0]["lastPrice"]
    return float(price)


def send_to_discord(price):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    message = {
        "content": f"🟣 ETH 当前价格: **{price} USDT**\n⏰ {now}"
    }

    requests.post(WEBHOOK_URL, json=message)


def main():
    price = get_eth_price()
    send_to_discord(price)


if __name__ == "__main__":
    main()
