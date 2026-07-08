#!/usr/bin/env python3
"""ウォッチリスト全銘柄の株価を取得し data/prices.json を生成する。

- データ源: Yahoo Finance (yfinance)。東証コードは「4063.T」形式。
- 出力: 直近終値 / 52週高値 / 52週高値からの下落率(%) / 取得日時
- 取得に失敗した銘柄は null で埋めて続行する（全体は止めない）。
"""
import json
import sys
import datetime
from pathlib import Path

import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST = ROOT / "data" / "watchlist.json"
OUT = ROOT / "data" / "prices.json"

JST = datetime.timezone(datetime.timedelta(hours=9), "JST")


def fetch_one(code: str):
    symbol = f"{code}.T"
    tk = yf.Ticker(symbol)
    hist = tk.history(period="1y", auto_adjust=False)
    if hist is None or hist.empty:
        raise ValueError(f"no data for {symbol}")
    close = float(hist["Close"].dropna().iloc[-1])
    high52 = float(hist["High"].dropna().max())
    if high52 <= 0:
        raise ValueError(f"invalid 52w high for {symbol}")
    drawdown = (close / high52 - 1.0) * 100.0
    return {
        "close": round(close, 1),
        "high52": round(high52, 1),
        "drawdown_pct": round(drawdown, 2),
        "asof": hist.index[-1].date().isoformat(),
    }


def main():
    watchlist = json.loads(WATCHLIST.read_text(encoding="utf-8"))
    prices = {}
    ok, ng = 0, []
    for item in watchlist:
        code = item["ticker"]
        try:
            prices[code] = fetch_one(code)
            ok += 1
            print(f"  {code} {item['name']}: OK ({prices[code]['drawdown_pct']}%)")
        except Exception as e:  # noqa: BLE001 - 失敗銘柄はnullで続行
            prices[code] = None
            ng.append(code)
            print(f"  {code} {item['name']}: FAILED ({e})", file=sys.stderr)

    out = {
        "generated_at": datetime.datetime.now(JST).isoformat(timespec="seconds"),
        "source": "Yahoo Finance (yfinance)",
        "prices": prices,
    }
    OUT.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"done: {ok} ok / {len(ng)} failed {ng if ng else ''}")


if __name__ == "__main__":
    main()
