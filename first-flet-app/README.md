# FirstFletApp app

## Run the app

### uv

Run as a desktop app:

```
uv run flet run
```

Run as a web app:

```
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://docs.flet.dev/).

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://docs.flet.dev/publish/android/).

---

## Market Watch — 实时指数与汇率 / Market Watch — Real-time Indices & FX

简要：基于 Flet 的轻量桌面应用，实时展示纳斯达克100（^NDX）、标普500（^GSPC）与中国银行人民币/美元买入/卖出价，界面显示最新数值与历史曲线。完整说明见 `README_market_watch.md`。

Summary: A lightweight Flet desktop app that fetches and displays Nasdaq-100 (^NDX), S&P 500 (^GSPC) and Bank of China USD/CNY buy & sell rates, showing live values and historical charts. See `README_market_watch.md` for full docs.

---

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://docs.flet.dev/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://docs.flet.dev/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://docs.flet.dev/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://docs.flet.dev/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://docs.flet.dev/publish/windows/).