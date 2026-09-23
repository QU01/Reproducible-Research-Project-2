"""Inject results + map geometry into the dashboard template -> dashboard/index.html"""
import json
from pathlib import Path

from geo import load_countries

ROOT = Path(__file__).resolve().parents[1]


def main():
    tpl = (ROOT / "dashboard" / "template.html").read_text()
    data = (ROOT / "results" / "dashboard_data.json").read_text()
    geo = json.dumps(load_countries(), separators=(",", ":"))
    text = json.load(open(ROOT / "dashboard" / "findings.json"))
    html = (tpl.replace("__DATA__", data).replace("__GEO__", geo)
            .replace("__FINDINGS__", json.dumps(text["findings"]))
            .replace("__LIMITS__", json.dumps(text["limits"])))
    out = ROOT / "dashboard" / "index.html"
    out.write_text(html)
    print(out, round(len(html) / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
