import requests
import datetime
import time

# ===== 配置 =====
WEBHOOK_URL = "DISCORD_WEBHOOK_URL"

BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=linear&symbol=ETHUSDT"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


# ===== 获取 Bybit 价格 =====
def get_eth_price_bybit():
    try:
        r = requests.get(BYBIT_URL, headers=HEADERS, timeout=10)

        print("Bybit 状态码:", r.status_code)

        if r.status_code != 200:
            raise Exception(f"HTTP错误: {r.status_code}")

        if not r.text:
            raise Exception("返回内容为空")

        data = r.json()

        if "result" not in data:
            raise Exception(f"API结构异常: {data}")

        price = data["result"]["list"][0]["lastPrice"]
        return float(price)

    except Exception as e:
        print("Bybit 获取失败:", e)
        return None


# ===== 获取 Binance 价格（备用） =====
def get_eth_price_binance():
    try:
        r = requests.get(BINANCE_URL, headers=HEADERS, timeout=10)

        print("Binance 状态码:", r.status_code)

        if r.status_code != 200:
            raise Exception(f"HTTP错误: {r.status_code}")

        data = r.json()
        return float(data["price"])

    except Exception as e:
        print("Binance 获取失败:", e)
        return None


# ===== 带重试机制 =====
def get_price_with_retry():
    for i in range(3):
        print(f"尝试获取价格 (第{i+1}次)")

        price = get_eth_price_bybit()
        if price is not None:
            print("✅ 使用 Bybit 数据")
            return price, "Bybit"

        time.sleep(2)

    # 👉 Bybit彻底失败 → 用Binance
    print("⚠️ Bybit失败，切换Binance")

    for i in range(3):
        print(f"尝试 Binance (第{i+1}次)")

        price = get_eth_price_binance()
        if price is not None:
            print("✅ 使用 Binance 数据")
            return price, "Binance"

        time.sleep(2)

    return None, None


# ===== 发送到 Discord =====
def send_to_discord(price, source):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if price is None:
        content = f"❌ ETH 获取失败（Bybit + Binance）\n⏰ {now}"
    else:
        content = (
            f"🟣 ETH 当前价格\n\n"
            f"💰 价格: **{price} USDT**\n"
            f"📡 数据源: {source}\n"
            f"⏰ {now}"
        )

    try:
        r = requests.post(WEBHOOK_URL, json={"content": content}, timeout=10)
        print("Discord 状态码:", r.status_code)
    except Exception as e:
        print("Discord 发送失败:", e)


# ===== 主函数 =====
def main():
    print("====== 启动 ETH 报价机器人 ======")

    price, source = get_price_with_retry()

    send_to_discord(price, source)

    print("====== 执行结束 ======")


if __name__ == "__main__":
    main()
