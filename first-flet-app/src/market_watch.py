import io
import threading
import time
from collections import deque
from datetime import datetime

import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import yfinance as yf
except Exception:
    yf = None

import flet as ft

# Simple market watch: Nasdaq100 (^NDX), S&P500 (^GSPC), BOC USD/CNY buy/sell
# Defaults: refresh every 60s, keep last 120 points

DEFAULT_INTERVAL = 60
MAX_POINTS = 120

class DataManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.timestamps = deque(maxlen=MAX_POINTS)
        self.ndx = deque(maxlen=MAX_POINTS)
        self.gspc = deque(maxlen=MAX_POINTS)
        self.usd_buy = deque(maxlen=MAX_POINTS)
        self.usd_sell = deque(maxlen=MAX_POINTS)

    def append(self, t, ndx, gspc, buy, sell):
        with self.lock:
            self.timestamps.append(t)
            self.ndx.append(ndx)
            self.gspc.append(gspc)
            self.usd_buy.append(buy)
            self.usd_sell.append(sell)

    def latest(self):
        with self.lock:
            return {
                "time": self.timestamps[-1] if self.timestamps else None,
                "ndx": self.ndx[-1] if self.ndx else None,
                "gspc": self.gspc[-1] if self.gspc else None,
                "buy": self.usd_buy[-1] if self.usd_buy else None,
                "sell": self.usd_sell[-1] if self.usd_sell else None,
            }

    def snapshot(self):
        with self.lock:
            return list(self.timestamps), list(self.ndx), list(self.gspc), list(self.usd_buy), list(self.usd_sell)


def fetch_index_price(symbol):
    if yf is None:
        raise RuntimeError("Missing dependency: yfinance. Install with `pip install yfinance`")
    try:
        t = yf.Ticker(symbol)
        # try fast_info
        try:
            v = t.fast_info.get("lastPrice")
            if v is not None:
                return float(v)
        except Exception:
            pass
        # fallback to history
        hist = t.history(period="1d", interval="1m")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception as e:
        print(f"fetch_index_price {symbol} error: {e}")
    return None


def fetch_boc_usd_cny():
    """Try to get Bank of China USD rates by scraping their public page. If fails, fallback to exchangerate.host midrate."""
    try:
        # Try Bank of China public search page (may change over time)
        url = "https://srh.bankofchina.com/search/whpj/search.jsp"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        text = r.text
        # find a line containing '美元' and three numeric rates: 含买入价/现汇买入/现汇卖出 (approx)
        import re
        m = re.search(r"美元[\s\S]{0,200}?(\d+\.\d+)[\s\S]{0,200}?(\d+\.\d+)[\s\S]{0,200}?(\d+\.\d+)", text)
        if m:
            # Empirical: groups may be [现汇买入价, 现汇卖出价, 中间价] orders vary; we'll take first two as buy/sell
            buy = float(m.group(1))
            sell = float(m.group(2))
            return buy, sell
    except Exception as e:
        print(f"BOC scrape failed: {e}")
    # fallback: use exchangerate.host for mid rate
    try:
        r = requests.get('https://api.exchangerate.host/latest?base=USD&symbols=CNY', timeout=10)
        r.raise_for_status()
        j = r.json()
        mid = j['rates']['CNY']
        # approximate bank spread
        buy = round(mid * 0.997, 6)
        sell = round(mid * 1.003, 6)
        return buy, sell
    except Exception as e:
        print(f"fallback exch rate failed: {e}")
    return None, None


def plot_snapshot(timestamps, ndx, gspc, buy, sell):
    fig, axes = plt.subplots(3, 1, figsize=(8, 6), constrained_layout=True)
    if timestamps:
        axes[0].plot(timestamps, ndx, '-o', linewidth=1)
        axes[0].set_title('Nasdaq100 (^NDX)')
        axes[1].plot(timestamps, gspc, '-o', linewidth=1, color='orange')
        axes[1].set_title('S&P500 (^GSPC)')
        axes[2].plot(timestamps, buy, '-o', linewidth=1, label='buy')
        axes[2].plot(timestamps, sell, '-o', linewidth=1, label='sell')
        axes[2].set_title('BOC RMB/USD (buy/sell)')
        axes[2].legend()
        for ax in axes:
            ax.tick_params(axis='x', rotation=30)
    else:
        axes[1].text(0.5, 0.5, 'No data yet', ha='center')
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def human_fmt(v):
    return f"{v:,.2f}" if v is not None else "—"


class MarketApp:
    def __init__(self, page: ft.Page, interval=DEFAULT_INTERVAL):
        self.page = page
        self.interval = interval
        self.dm = DataManager()
        self.running = False
        # UI components
        self.ndx_text = ft.Text('—', size=18, weight=ft.FontWeight.BOLD)
        self.gspc_text = ft.Text('—', size=18, weight=ft.FontWeight.BOLD)
        self.usd_text = ft.Text('—', size=18, weight=ft.FontWeight.BOLD)
        self.plot_image = ft.Image(src='', width=800, height=600)
        self.status = ft.Text('初始化...', size=12)
        self._build_ui()

    def _build_ui(self):
        controls = ft.Row([
            ft.Column([
                ft.Text('Nasdaq 100', size=12),
                self.ndx_text
            ], alignment=ft.MainAxisAlignment.START),
            ft.Column([
                ft.Text('S&P 500', size=12),
                self.gspc_text
            ], alignment=ft.MainAxisAlignment.START),
            ft.Column([
                ft.Text('BOC USD/CNY', size=12),
                self.usd_text
            ], alignment=ft.MainAxisAlignment.START),
            ft.Column([
                ft.Row([
                    ft.Text('自动刷新 (秒):'),
                    (lambda: (lambda dd: (setattr(dd, 'on_change', self.on_interval_change), dd)[1])(ft.Dropdown(width=100, value=str(self.interval), options=[ft.dropdown.Option(str(x)) for x in [15,30,60,120]])) )()
                ])
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.page.add(controls)
        self.page.add(self.plot_image)
        self.page.add(self.status)

    def on_interval_change(self, e):
        try:
            self.interval = int(e.control.value)
            self.status.value = f"刷新间隔设置为 {self.interval} 秒"
            self.page.update()
        except Exception as ex:
            print('interval change error', ex)

    def start(self):
        if not self.running:
            self.running = True
            t = threading.Thread(target=self._loop, daemon=True)
            t.start()

    def stop(self):
        self.running = False

    def _loop(self):
        # initial backfill: try to fetch a recent price sample
        while self.running:
            t = datetime.now()
            ndx = fetch_index_price('^NDX')
            gspc = fetch_index_price('^GSPC')
            buy, sell = fetch_boc_usd_cny()
            if ndx is None and gspc is None and buy is None:
                self.status.value = f"获取数据失败，{t.strftime('%H:%M:%S')}，稍后重试"
                self.page.update()
            else:
                self.dm.append(t, ndx if ndx is not None else (self.dm.ndx[-1] if self.dm.ndx else None),
                               gspc if gspc is not None else (self.dm.gspc[-1] if self.dm.gspc else None),
                               buy if buy is not None else (self.dm.usd_buy[-1] if self.dm.usd_buy else None),
                               sell if sell is not None else (self.dm.usd_sell[-1] if self.dm.usd_sell else None))
                latest = self.dm.latest()
                self.ndx_text.value = human_fmt(latest['ndx'])
                self.gspc_text.value = human_fmt(latest['gspc'])
                if latest['buy'] is not None and latest['sell'] is not None:
                    self.usd_text.value = f"买 {latest['buy']:.4f} / 卖 {latest['sell']:.4f}"
                else:
                    self.usd_text.value = '—'
                # render plot
                ts, ndx_l, gspc_l, buy_l, sell_l = self.dm.snapshot()
                png = plot_snapshot(ts, ndx_l, gspc_l, buy_l, sell_l)
                import base64
                b64 = base64.b64encode(png).decode('ascii')
                self.plot_image.src_base64 = b64
                self.status.value = f"上次更新时间：{t.strftime('%Y-%m-%d %H:%M:%S')}，数据点：{len(ts)}"
                self.page.update()
            # sleep but allow interval change
            slept = 0
            while self.running and slept < self.interval:
                time.sleep(1)
                slept += 1


def main(page: ft.Page):
    page.title = 'Market Watch — 实时指数与汇率'
    app = MarketApp(page)
    app.start()


if __name__ == '__main__':
    ft.app(target=main)
