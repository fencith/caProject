# Market Watch — 实时指数与汇率 / Market Watch — Real-time Indices & FX

📌 简短说明（中文）

Market Watch 是一个使用 Flet 构建的轻量桌面应用，实时获取并展示纳斯达克100 指数（^NDX）、标普500 指数（^GSPC）以及中国银行人民币对美元的买入/卖出牌价（若无法抓取银行牌价，回退到 exchangerate.host 的中间价并加小幅差值）。界面显示最新数值和历史曲线（可选刷新间隔）。

Short description (English)

Market Watch is a lightweight Flet desktop app that fetches and displays live Nasdaq-100 (^NDX), S&P 500 (^GSPC) and Bank of China USD/CNY buy & sell rates. If bank rates cannot be scraped, it falls back to exchangerate.host mid-rate with a small simulated spread. The UI shows current values and time-series charts, with adjustable refresh interval.

---

## 主要特性 / Features ✅

- 实时拉取：^NDX、^GSPC、BOC USD/CNY（买/卖）
- 图表：使用 Matplotlib 绘制历史曲线并以 PNG 显示于界面
- 可调整刷新间隔（15 / 30 / 60 / 120 秒）
- 容错：yfinance 限制或 BOC 页面不可用时有降级策略

- Live fetch for ^NDX, ^GSPC, and BOC USD/CNY
- Plots history using Matplotlib and renders in the Flet UI
- Adjustable refresh interval (15/30/60/120 sec)
- Graceful fallback when yfinance or BOC scraping is unavailable

---

## 依赖 / Requirements

- Python 3.10+（已在本机用 3.12 / 3.14 测试）
- Python 包：flet, yfinance, matplotlib, requests, Pillow

安装依赖（示例）：

```bash
python3 -m pip install --user flet yfinance matplotlib requests Pillow
```

---

## 运行（本地桌面） / Run (desktop)

1. 启动（开发）：

```bash
uv run flet run
# 或者直接运行模块
python3 -m src.market_watch
```

2. 默认行为：会每 60 秒刷新（首次运行后会逐步积累历史点）。

---

## 配置与提示 / Configuration & Notes

- 刷新间隔可在 UI 顶部下拉中调整（15/30/60/120 秒）。
- 如果你在公司/受限网络，请先确保能访问 `https://repo.maven.apache.org/`（用于 Flutter/Android 打包），或配置网络代理以便构建 Android 包。
- yfinance 可能会触发速率限制（Too Many Requests），建议用于开发和小规模监控；若需要高可用或高频实时数据，请考虑付费 API（如 Polygon、IEX、AlphaVantage 等）。
- 中国银行网站结构可能变化，抓取失败时应用会退到 `exchangerate.host` 的中间价并用小幅差值作为买/卖价近似。

- Refresh interval is adjustable via the UI (15/30/60/120 sec).
- If you are behind a corporate network, ensure internet access to external repos or configure a proxy for download/build operations.
- yfinance is rate-limited; for production-grade real-time data consider paid market data APIs.
- BOC scraping may break if the bank's site changes; a fallback to exchangerate.host is provided.

---

## 常见问题 / Troubleshooting

- 若 `uv run flet run` 报 `permission denied` 写入缓存，可运行：

```bash
chmod -R u+rwx ~/.cache/uv
```

- 若启动时报网络超时（Gradle / Maven 依赖下载失败），请检查网络或代理设置。

- 如果需要在 Android 上打包，确保已安装 Android SDK、cmdline-tools、并设置 `ANDROID_SDK_ROOT`/`ANDROID_HOME` 与 `JAVA_HOME`（见项目根 README 的 Android 说明）。

---

## 开发 & 扩展建议 / Development & Improvements

- 持久化历史到本地（JSON/SQLite）以便重启后保留图表历史。建议添加 `data/market_history.json` 写入/导出逻辑。 
- 集成稳定的付费行情/外汇 API（并支持 API key 配置）。
- 增强 UI：图表缩放、选择时间窗口、导出 CSV。

---

## 文件位置 / Files

- 主程序：`src/market_watch.py`
- 入口：`src/main.py`

---

## 许可证 / License

本 README 遵循项目原有许可（请参见仓库根目录 LICENSE）。

---

如需我把 README 合并到根 `README.md` 或生成中文/英文各自独立的 README，我可以再按你的偏好调整并提交。