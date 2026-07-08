#!/usr/bin/env python3
"""PWAアイコン生成（純Python・PIL不要）。

ダーク地に、52週高値からの下落と−25%/−40%の閾値ラインを模した
シンプルな幾何モチーフを描く。icon-180/192/512.png を出力。
"""
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BG = (18, 22, 28)        # #12161c
LINE = (122, 162, 247)   # 下落ポリライン（青）
AMBER = (224, 160, 50)   # -25% 打診圏
RED = (214, 88, 80)      # -40% 二段目圏


def write_png(path, size, pixels):
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))

    raw = b"".join(
        b"\x00" + bytes(v for px in row for v in px) for row in pixels
    )
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def make_icon(size):
    px = [[BG for _ in range(size)] for _ in range(size)]
    m = size / 100.0  # 100x100座標系で描く

    def hline(y, x0, x1, color, w):
        y0, y1 = int((y - w / 2) * m), int((y + w / 2) * m)
        for yy in range(max(0, y0), min(size, y1 + 1)):
            for xx in range(int(x0 * m), int(x1 * m)):
                px[yy][xx] = color

    def polyline(points, color, w):
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            steps = int(max(abs(bx - ax), abs(by - ay)) * m * 2) + 1
            for i in range(steps + 1):
                t = i / steps
                cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
                r = w * m / 2
                for yy in range(int((cy) * m - r), int((cy) * m + r) + 1):
                    for xx in range(int((cx) * m - r), int((cx) * m + r) + 1):
                        if 0 <= xx < size and 0 <= yy < size:
                            if (xx - cx * m) ** 2 + (yy - cy * m) ** 2 <= r * r:
                                px[yy][xx] = color

    # 閾値ライン（-25%: 琥珀 / -40%: 赤）
    hline(55, 14, 86, AMBER, 2.4)
    hline(72, 14, 86, RED, 2.4)
    # 高値からの下落ポリライン
    polyline([(16, 30), (34, 38), (46, 33), (62, 58), (72, 52), (84, 76)], LINE, 5)
    return px


def main():
    for size in (180, 192, 512):
        out = ROOT / f"icon-{size}.png"
        write_png(out, size, make_icon(size))
        print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
