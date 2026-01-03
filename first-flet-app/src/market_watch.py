import io
import threading
import time
from collections import deque
from datetime import datetime

import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import random

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
    """Try multiple methods: HTML scrape (Yahoo), Stooq CSV, yfinance, Yahoo APIs."""
    # try HTML scrape from Yahoo (may bypass API rate limits)
    try:
        sym_enc = symbol.replace('^', '%5E')
        url = f"https://finance.yahoo.com/quote/{sym_enc}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MarketWatchBot/1.0)"}
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        # try fin-streamer with data-field
        fs = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        if fs and fs.text:
            try:
                return float(fs.text.replace(',', ''))
            except Exception:
                pass
        # fallback: look for spans with regex class
        spans = soup.find_all('span')
        for s in spans:
            txt = (s.text or '').strip()
            if txt and all(c.isdigit() or c in '.,' for c in txt):
                try:
                    return float(txt.replace(',', ''))
                except Exception:
                    continue
    except Exception as e:
        print(f"fetch_index_price html scrape failed: {e}")
    # fallback: stooq CSV using ETF proxies when indices aren't available
    try:
        # use ETF proxies: QQQ ~ Nasdaq100, SPY ~ S&P500
        name_map = {'^NDX': 'qqq.us', '^GSPC': 'spy.us'}
        sname = name_map.get(symbol, None)
        if sname:
            csv_url = f"https://stooq.com/q/l/?s={sname}&f=sd2t2ohlcvn&h&e=csv"
            r = requests.get(csv_url, timeout=10)
            r.raise_for_status()
            text = r.text.strip().splitlines()
            if len(text) >= 2:
                vals = text[1].split(',')
                # columns: Symbol,Date,Time,Open,High,Low,Close,Volume,Name
                close = vals[6] if len(vals) > 6 else None
                if close and close != 'N/D':
                    print(f"fetch_index_price stooq-etf {sname} close={close}")
                    return float(close)
    except Exception as e:
        print(f"fetch_index_price stooq failed: {e}")
    # try yfinance as before
    if yf is not None:
        try:
            t = yf.Ticker(symbol)
            try:
                v = t.fast_info.get("lastPrice")
                if v is not None:
                    return float(v)
            except Exception:
                pass
            hist = t.history(period="1d", interval="1m")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
        except Exception as e:
            print(f"fetch_index_price {symbol} error: {e}")
    # fallback: try Yahoo public quote API directly (last resort)
    try:
        r = requests.get("https://query1.finance.yahoo.com/v7/finance/quote", params={"symbols": symbol}, timeout=10)
        r.raise_for_status()
        j = r.json()
        res = j.get('quoteResponse', {}).get('result', [])
        if res:
            price = res[0].get('regularMarketPrice') or res[0].get('regularMarketPreviousClose')
            if price is not None:
                return float(price)
    except Exception as e:
        print(f"fetch_index_price fallback yahoo failed: {e}")
    return None


def fetch_boc_usd_cny():
    """Try multiple HTML sources for USD/CNY: BOC page, X-Rates, Stooq CSV, exchangerate.host."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MarketWatchBot/1.0)"}
    try:
        # Try BOC first (older URL may change)
        url = "https://www.boc.cn/sourcedb/whpj/"
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        # find USD row
        rows = soup.find_all('tr')
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
            if cols and ('美元' in ''.join(cols) or 'USD' in ''.join(cols)):
                # find numeric values in cols
                import re
                nums = re.findall(r"\d+\.\d+", ' '.join(cols))
                if len(nums) >= 2:
                    buy = float(nums[0])
                    sell = float(nums[1])
                    return buy, sell
    except Exception as e:
        print(f"BOC scrape failed: {e}")
    # try X-Rates HTML
    try:
        url = 'https://www.x-rates.com/calculator/?from=USD&to=CNY&amount=1'
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        out = soup.select_one('.ccOutputRslt')
        if out and out.text:
            txt = out.text.strip()
            # e.g. '6.97 Chinese Yuan'
            parts = txt.split(' ')
            rate = float(parts[0].replace(',', ''))
            buy = round(rate * 0.997, 6)
            sell = round(rate * 1.003, 6)
            return buy, sell
    except Exception as e:
        print(f"x-rates scrape failed: {e}")
    # try stooq CSV for forex
    try:
        r = requests.get('https://stooq.com/q/l/?s=usdcny&f=sd2t2ohlcvn&h&e=csv', timeout=10)
        r.raise_for_status()
        text = r.text.strip().splitlines()
        if len(text) >= 2:
            vals = text[1].split(',')
            close = vals[6] if len(vals) > 6 else None
            if close and close != 'N/D':
                rate = float(close)
                buy = round(rate * 0.997, 6)
                sell = round(rate * 1.003, 6)
                return buy, sell
    except Exception as e:
        print(f"stooq forex failed: {e}")
    # final fallback: exchangerate.host
    try:
        r = requests.get('https://api.exchangerate.host/latest?base=USD&symbols=CNY', timeout=10)
        r.raise_for_status()
        j = r.json()
        mid = j.get('rates', {}).get('CNY')
        if mid:
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
        self.source_text = ft.Text('', size=11)
        # initial transparent 1x1 PNG as placeholder to satisfy Flet's src requirement
        # use a valid data URL placeholder so Flet won't reject an empty src
        placeholder_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
        self.plot_image = ft.Image(src=f'data:image/png;base64,{placeholder_b64}', width=800, height=600)
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
            ]),
            ft.Column([
                ft.Row([
                    ft.ElevatedButton('刷新', on_click=self.on_manual_refresh),
                    self.source_text
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

    def on_manual_refresh(self, e):
        # spawn a short-lived thread to perform one immediate fetch to keep UI responsive
        t = threading.Thread(target=self._single_fetch, daemon=True)
        t.start()

    def _single_fetch(self):
        t = datetime.now()
        ndx = fetch_index_price('^NDX')
        gspc = fetch_index_price('^GSPC')
        buy, sell = fetch_boc_usd_cny()
        print(f"MANUAL FETCH: ndx={ndx}, gspc={gspc}, buy={buy}, sell={sell}")
        if ndx is None and gspc is None and buy is None:
            self.status.value = f"手动刷新：获取数据失败，{t.strftime('%H:%M:%S')}"
            self.page.update()
            return
        self.dm.append(t,
                       ndx if ndx is not None else (self.dm.ndx[-1] if self.dm.ndx else None),
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
        ts, ndx_l, gspc_l, buy_l, sell_l = self.dm.snapshot()
        png = plot_snapshot(ts, ndx_l, gspc_l, buy_l, sell_l)
        import base64
        b64 = base64.b64encode(png).decode('ascii')
        self.plot_image.src = f"data:image/png;base64,{b64}"
        srcs = []
        if ndx is not None:
            srcs.append('index-html')
        if buy is not None:
            srcs.append('fx-html')
        self.source_text.value = '来源:' + (', '.join(srcs) if srcs else '未知')
        self.status.value = f"手动刷新：{t.strftime('%Y-%m-%d %H:%M:%S')}，数据点：{len(ts)}"
        self.page.update()

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
            ndx = gspc = buy = sell = None
            # retry loop with small backoff to handle transient failures / rate limits
            for attempt in range(1, 4):
                ndx = fetch_index_price('^NDX')
                gspc = fetch_index_price('^GSPC')
                buy, sell = fetch_boc_usd_cny()
                # Debug: log raw fetched values so we can see why '实时' 没有更新
                print(f"DEBUG FETCH: ndx={ndx}, gspc={gspc}, buy={buy}, sell={sell}")
                # update source_text to help understanding where data came from
                srcs = []
                if ndx is not None:
                    srcs.append('index-html')
                if buy is not None:
                    srcs.append('fx-html')
                self.source_text.value = '来源:' + (', '.join(srcs) if srcs else '未知')
                if ndx is not None or gspc is not None or buy is not None:
                    break
                # transient failure: update status and backoff a bit
                if attempt < 3:
                    backoff = attempt * 1.0 + random.random() * 0.5
                    self.status.value = f"尝试第{attempt}次获取数据失败，{t.strftime('%H:%M:%S')}，{backoff:.1f}s 后重试"
                    self.page.update()
                    time.sleep(backoff)
            # if still all None
            if ndx is None and gspc is None and buy is None:
                if self.dm.timestamps:
                    # use last-known values so UI stays alive
                    latest = self.dm.latest()
                    ndx = latest['ndx']
                    gspc = latest['gspc']
                    buy = latest['buy']
                    sell = latest['sell']
                    self.dm.append(t, ndx, gspc, buy, sell)
                    ts, ndx_l, gspc_l, buy_l, sell_l = self.dm.snapshot()
                    png = plot_snapshot(ts, ndx_l, gspc_l, buy_l, sell_l)
                    import base64
                    b64 = base64.b64encode(png).decode('ascii')
                    self.plot_image.src = f"data:image/png;base64,{b64}"
                    self.ndx_text.value = human_fmt(ndx)
                    self.gspc_text.value = human_fmt(gspc)
                    if buy is not None and sell is not None:
                        self.usd_text.value = f"买 {buy:.4f} / 卖 {sell:.4f}"
                    else:
                        self.usd_text.value = '—'
                    self.status.value = f"使用缓存数据（上次成功） — {t.strftime('%Y-%m-%d %H:%M:%S')}"
                    self.page.update()
                else:
                    self.status.value = f"获取数据失败（无历史数据），{t.strftime('%H:%M:%S')}，稍后重试"
                    self.page.update()
                    time.sleep(1)
                    continue
            else:
                # append fetched values, substituting per-field last-known values when needed
                self.dm.append(t,
                               ndx if ndx is not None else (self.dm.ndx[-1] if self.dm.ndx else None),
                               gspc if gspc is not None else (self.dm.gspc[-1] if self.dm.gspc else None),
                               buy if buy is not None else (self.dm.usd_buy[-1] if self.dm.usd_buy else None),
                               sell if sell is not None else (self.dm.usd_sell[-1] if self.dm.usd_sell else None))
                latest = self.dm.latest()
                self.ndx_text.value = human_fmt(latest['ndx'])
                self.gspc_text.value = human_fmt(latest['gspc'])
                print(f"UI UPDATE: ndx_text={self.ndx_text.value}, gspc_text={self.gspc_text.value}")
                if latest['buy'] is not None and latest['sell'] is not None:
                    self.usd_text.value = f"买 {latest['buy']:.4f} / 卖 {latest['sell']:.4f}"
                else:
                    self.usd_text.value = '—'
                # render plot
                ts, ndx_l, gspc_l, buy_l, sell_l = self.dm.snapshot()
                png = plot_snapshot(ts, ndx_l, gspc_l, buy_l, sell_l)
                import base64
                b64 = base64.b64encode(png).decode('ascii')
                # assign data URL to `src` so Flet can render the image
                self.plot_image.src = f"data:image/png;base64,{b64}"
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
