#!/usr/bin/env python3
"""
auth_heatmap.py
---------------
*This script generated completely by Claude AI. I did not write or edit this code aside from this statement.*
Parse an auth.log, extract attacker IPs, geolocate them via
ipgeolocation.io, and render a Folium heatmap HTML file — all in one shot.

Dependencies:
    pip install folium

Usage:
    python3 auth_heatmap.py /var/log/auth.log
    python3 auth_heatmap.py /var/log/auth.log --out report.html
    python3 auth_heatmap.py /var/log/auth.log --top 200 --csv backup.csv
"""

import re
import sys
import csv
import json
import time
import argparse
import ipaddress
from collections import Counter
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

try:
    import folium
    from folium.plugins import HeatMap, MarkerCluster
except ImportError:
    sys.exit(
        "[ERROR] folium is not installed.\n"
        "        Run:  pip install folium\n"
        "        Then try again."
    )

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY      = "b0a9124f89fd4cbeae1111756975c152"
API_ENDPOINT = "https://api.ipgeolocation.io/ipgeo"
RATE_LIMIT_S = 0.35   # ~3 req/s — free tier is 1 req/s sustained, 1k/day

IP_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

INTERESTING_RE = re.compile(
    r"(Failed password|Invalid user|authentication failure|"
    r"Connection closed|Received disconnect|"
    r"Bad protocol|Did not receive|PAM|BREAK-IN|refused connect)",
    re.IGNORECASE,
)

# ── Log parsing ───────────────────────────────────────────────────────────────

def is_public(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
        return not (addr.is_private or addr.is_loopback or addr.is_link_local
                    or addr.is_multicast or addr.is_reserved or addr.is_unspecified)
    except ValueError:
        return False


def parse_auth_log(path: str) -> Counter:
    counts: Counter = Counter()
    try:
        with open(path, "r", errors="replace") as fh:
            for line in fh:
                if not INTERESTING_RE.search(line):
                    continue
                for ip in IP_RE.findall(line):
                    if is_public(ip):
                        counts[ip] += 1
    except FileNotFoundError:
        sys.exit(f"[ERROR] File not found: {path}")
    except PermissionError:
        sys.exit(f"[ERROR] Permission denied — try:  sudo python3 {sys.argv[0]} ...")
    return counts

# ── Geolocation ───────────────────────────────────────────────────────────────

def geolocate(ip: str) -> dict:
    url = f"{API_ENDPOINT}?apiKey={API_KEY}&ip={ip}&fields=geo,isp"
    try:
        req  = Request(url, headers={"User-Agent": "auth-heatmap/1.0"})
        resp = urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        lat  = data.get("latitude")
        lon  = data.get("longitude")
        if not lat or not lon:
            return None
        return {
            "ip":           ip,
            "latitude":     float(lat),
            "longitude":    float(lon),
            "country":      data.get("country_name", ""),
            "country_code": data.get("country_code2", ""),
            "state":        data.get("state_prov", ""),
            "city":         data.get("city", ""),
            "isp":          data.get("isp", ""),
            "organization": data.get("organization", ""),
        }
    except HTTPError as e:
        if e.code == 423:
            print("\n  [WARN] API quota exhausted — flushing what we have.")
            raise
        print(f"  [WARN] {ip}: HTTP {e.code}")
        return None
    except (URLError, ValueError) as e:
        print(f"  [WARN] {ip}: {e}")
        return None

# ── CSV backup ────────────────────────────────────────────────────────────────

def write_csv(records: list, path: str):
    fields = ["ip", "hit_count", "latitude", "longitude",
              "city", "state", "country", "country_code", "isp", "organization"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    print(f"  CSV saved -> {path}")

# ── Folium map ────────────────────────────────────────────────────────────────

def build_map(records: list, log_path: str) -> folium.Map:
    total_w  = sum(r["hit_count"] for r in records) or 1
    mean_lat = sum(r["latitude"]  * r["hit_count"] for r in records) / total_w
    mean_lon = sum(r["longitude"] * r["hit_count"] for r in records) / total_w
    max_hits = max(r["hit_count"] for r in records)

    m = folium.Map(
        location=[mean_lat, mean_lon],
        zoom_start=2,
        tiles="CartoDB dark_matter",
    )

    # ── Heatmap layer ─────────────────────────────────────────────────────────
    HeatMap(
        [[r["latitude"], r["longitude"], r["hit_count"] / max_hits] for r in records],
        name="Heatmap",
        min_opacity=0.3,
        max_zoom=8,
        radius=18,
        blur=14,
        gradient={0.2: "blue", 0.45: "cyan", 0.65: "lime", 0.85: "yellow", 1.0: "red"},
    ).add_to(m)

    # ── Marker cluster layer ──────────────────────────────────────────────────
    cluster = MarkerCluster(name="Individual IPs").add_to(m)
    for r in records:
        location   = f"{r['city']}, {r['state']}" if r["city"] else r["country"]
        org_line   = r["organization"] or r["isp"] or "Unknown"
        popup_html = f"""
            <div style="font-family:monospace;min-width:200px">
                <b>{r['ip']}</b><br>
                <hr style="margin:4px 0">
                {location}<br>
                {r['country']} ({r['country_code']})<br>
                {org_line}<br>
                <hr style="margin:4px 0">
                <b>{r['hit_count']}</b> auth hit{'s' if r['hit_count'] != 1 else ''}
            </div>
        """
        color = ("red"    if r["hit_count"] >= max_hits * 0.5  else
                 "orange" if r["hit_count"] >= max_hits * 0.1  else
                 "blue")
        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{r['ip']} ({r['hit_count']} hits)",
            icon=folium.Icon(color=color, icon="exclamation-sign"),
        ).add_to(cluster)

    folium.LayerControl(collapsed=False).add_to(m)

    title_html = f"""
        <div style="
            position:fixed; top:10px; left:50%; transform:translateX(-50%);
            z-index:1000; background:rgba(0,0,0,0.75); color:white;
            padding:10px 20px; border-radius:8px;
            font-family:monospace; font-size:14px; pointer-events:none;">
            Auth Attack Map |
            <b>{len(records)}</b> IPs |
            <b>{sum(r['hit_count'] for r in records)}</b> total hits |
            {log_path}
        </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))
    return m

# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(records: list):
    countries = Counter(r["country"] for r in records if r.get("country"))
    print("\n── Top attacking countries ──────────────────────")
    for country, cnt in countries.most_common(10):
        bar = "█" * min(cnt, 40)
        print(f"  {country:<30} {cnt:>4}  {bar}")
    print("─────────────────────────────────────────────────")
    print(f"  IPs geolocated : {len(records)}")
    print(f"  Total hits     : {sum(r['hit_count'] for r in records)}")
    print(f"  Countries seen : {len(countries)}\n")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="auth.log -> Folium heatmap")
    parser.add_argument("logfile",        help="Path to auth.log")
    parser.add_argument("--out",   "-o",  default="auth_heatmap.html",
                        help="Output HTML file (default: auth_heatmap.html)")
    parser.add_argument("--top",   "-n",  type=int, default=0,
                        help="Geolocate only the top N IPs by hit count (0 = all)")
    parser.add_argument("--csv",          default="",
                        help="Also write a CSV backup alongside the map")
    args = parser.parse_args()

    # 1. Parse ─────────────────────────────────────────────────────────────────
    print(f"\n[1/3] Parsing {args.logfile} ...")
    ip_counts = parse_auth_log(args.logfile)
    if not ip_counts:
        sys.exit("[!] No public IPs found. Is this a real auth.log?")

    ordered = ip_counts.most_common(args.top if args.top > 0 else None)
    print(f"      {len(ordered)} unique public IPs "
          f"({sum(ip_counts.values())} total hits)")

    # 2. Geolocate ─────────────────────────────────────────────────────────────
    print(f"\n[2/3] Geolocating {len(ordered)} IPs ...")
    records = []
    width   = len(str(len(ordered)))
    for idx, (ip, count) in enumerate(ordered, 1):
        print(f"  [{idx:>{width}}/{len(ordered)}] {ip:<16} (hits: {count:>5})", end="  ")
        try:
            geo = geolocate(ip)
        except HTTPError:
            break
        if geo is None:
            print("-> skipped")
            continue
        geo["hit_count"] = count
        records.append(geo)
        print(f"-> {geo['city'] or '?'}, {geo['country_code'] or '?'}")
        time.sleep(RATE_LIMIT_S)

    if not records:
        sys.exit("[!] No records geolocated. Check API key / quota.")

    # 3. Render ────────────────────────────────────────────────────────────────
    print(f"\n[3/3] Building map ...")
    m = build_map(records, args.logfile)
    m.save(args.out)
    print(f"  Map saved -> {args.out}  (open in any browser)")

    if args.csv:
        write_csv(records, args.csv)

    print_summary(records)


if __name__ == "__main__":
    main()
