#!/usr/bin/env python3
"""
cf_division_ladder.py
Fetch Codeforces problems, detect division (Div1/Div2/Div3/Div4) from contest names,
filter by index (A-F) and rating (exact or range), exclude already solved problems,
and output CSV + HTML ladders.

Usage examples:
  python cf_division_ladder.py --divisions div2 --indices A B C D E F --rating 1200
  python cf_division_ladder.py --divisions div1 div2 div3 div4 --indices A B C --range 800 1400 --combine
  python cf_division_ladder.py --divisions div1 div2 div3 div4 --indices A B C D E F --range 800 3500 --handle TellMeTrue
"""

import argparse
import csv
import html
import os
import re
import sys
from typing import Dict, List, Tuple, Optional
import requests

PROBLEMS_URL = "https://codeforces.com/api/problemset.problems"
CONTESTS_URL = "https://codeforces.com/api/contest.list"
USER_SUBMISSIONS_URL = "https://codeforces.com/api/user.status"

# ---------------------- Fetch data ----------------------

def fetch_contests() -> Dict[int, str]:
    r = requests.get(CONTESTS_URL, params={"gym": False}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        raise RuntimeError("Failed to fetch contests from Codeforces API")
    return {c["id"]: c.get("name", "") for c in data["result"]}

def fetch_problemset() -> Tuple[List[dict], Dict[Tuple[int, str], int]]:
    r = requests.get(PROBLEMS_URL, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        raise RuntimeError("Failed to fetch problems from Codeforces API")
    problems = data["result"]["problems"]
    stats = data["result"].get("problemStatistics", [])
    solved_map = {}
    for s in stats:
        solved_map[(s["contestId"], s["index"])] = s.get("solvedCount", 0)
    return problems, solved_map

def fetch_solved_problems(handle: str) -> set:
    """Return set of (contestId, index) for problems the user has solved."""
    url = f"{USER_SUBMISSIONS_URL}?handle={handle}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        raise RuntimeError(f"Failed to fetch submissions for handle {handle}")
    solved = set()
    for sub in data["result"]:
        if sub.get("verdict") == "OK":
            pid = sub.get("problem", {})
            solved.add((pid.get("contestId"), pid.get("index")))
    return solved

# ---------------------- Filtering ----------------------

def detect_division_from_contest_name(name: str) -> Optional[str]:
    if not name:
        return None
    m = re.search(r"div(?:\.|\s)?\s*([1-4])", name, flags=re.I)
    if m:
        return f"div{m.group(1)}"
    m2 = re.search(r"division\s*([1-4])", name, flags=re.I)
    if m2:
        return f"div{m2.group(1)}"
    return None

def matches_index(idx: str, wanted_prefixes: List[str]) -> bool:
    idx = (idx or "").upper()
    for pref in wanted_prefixes:
        if idx.startswith(pref.upper()):
            return True
    return False

def filter_and_annotate(
    problems: List[dict],
    solved_map: Dict[Tuple[int, str], int],
    contest_map: Dict[int, str],
    wanted_divisions: List[str],
    wanted_indices: List[str],
    exact_rating: Optional[int],
    min_rating: Optional[int],
    max_rating: Optional[int],
    solved_set: Optional[set] = None,
) -> List[dict]:
    wanted_divisions = [d.lower() for d in (wanted_divisions or [])]
    wanted_indices = [i.upper() for i in (wanted_indices or [])]
    rows = []
    for p in problems:
        if "rating" not in p:
            continue
        idx = p.get("index", "")
        if not matches_index(idx, wanted_indices):
            continue
        r = p["rating"]
        if exact_rating is not None:
            if r != exact_rating:
                continue
        else:
            if min_rating is not None and r < min_rating:
                continue
            if max_rating is not None and r > max_rating:
                continue
        cid = p.get("contestId")
        if solved_set and (cid, idx) in solved_set:
            continue  # skip solved problems
        contest_name = contest_map.get(cid, "")
        division = detect_division_from_contest_name(contest_name)
        if wanted_divisions and (division is None or division.lower() not in wanted_divisions):
            continue
        sc = solved_map.get((cid, idx), 0)
        link = f"https://codeforces.com/contest/{cid}/problem/{idx}"
        rows.append({
            "contestId": cid,
            "contestName": contest_name,
            "index": idx,
            "name": p.get("name", ""),
            "rating": r,
            "tags": p.get("tags", []),
            "solvedCount": sc,
            "link": link,
            "division": division or "unknown",
        })
    return rows

# ---------------------- Sorting & Output ----------------------

def sort_rows(rows: List[dict], sort_key: str) -> List[dict]:
    if sort_key == "solved":
        return sorted(rows, key=lambda x: (-x["solvedCount"], x["rating"], x["contestId"], x["index"]))
    if sort_key == "rating":
        return sorted(rows, key=lambda x: (x["rating"], x["contestId"], x["index"]))
    if sort_key == "newest":
        return sorted(rows, key=lambda x: (-x["contestId"], x["index"]))
    if sort_key == "oldest":
        return sorted(rows, key=lambda x: (x["contestId"], x["index"]))
    return rows

def write_csv(path: str, rows: List[dict]):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "contestId", "contestName", "index", "name", "rating", "solvedCount", "tags", "link", "division"])
        for i, r in enumerate(rows, 1):
            w.writerow([
                i, r["contestId"], r["contestName"], r["index"], r["name"], r["rating"],
                r["solvedCount"], ";".join(r["tags"]), r["link"], r["division"]
            ])

def write_html(path: str, rows: List[dict], title: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    def esc(s: str) -> str:
        return html.escape(str(s), quote=True)
    head = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;margin:20px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;vertical-align:top}}
th{{background:#f5f5f5;text-align:left}}
tr:nth-child(even){{background:#fafafa}}
.tag{{display:inline-block;padding:2px 6px;border-radius:10px;border:1px solid #ccc;margin:2px;font-size:12px}}
</style>
</head>
<body>
<h1>{esc(title)}</h1>
<table>
<thead><tr><th>#</th><th>Problem</th><th>Contest</th><th>Rating</th><th>Solved</th><th>Tags</th><th>Division</th></tr></thead>
<tbody>
"""
    rows_html = []
    for i, r in enumerate(rows, 1):
        tags_html = " ".join(f"<span class='tag'>{esc(t)}</span>" for t in r["tags"])
        rows_html.append(
            f"<tr><td>{i}</td>"
            f"<td><a href='{esc(r['link'])}' target='_blank' rel='noopener'>{esc(r['contestId'])}{esc(r['index'])} — {esc(r['name'])}</a></td>"
            f"<td>{esc(r['contestName'])}</td>"
            f"<td>{esc(r['rating'])}</td>"
            f"<td>{esc(r['solvedCount'])}</td>"
            f"<td>{tags_html}</td>"
            f"<td>{esc(r['division'])}</td>"
            f"</tr>"
        )
    foot = "</tbody></table></body></html>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(rows_html) + foot)

# ---------------------- CLI ----------------------

def parse_args():
    p = argparse.ArgumentParser(description="Build Codeforces ladders by division, index and rating.")
    p.add_argument("--divisions", "-d", nargs="+", choices=["div1", "div2", "div3", "div4"],
                   help="Divisions to include (div1 div2 ...). If omitted, includes all detected divisions.")
    p.add_argument("--indices", "-i", nargs="+", default=["A", "B", "C", "D", "E", "F"],
                   help="Problem indices (A B C ...). Default: A B C D E F")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--rating", type=int, help="Exact rating (e.g., 1200)")
    group.add_argument("--range", nargs=2, type=int, metavar=("MIN", "MAX"), help="Rating range inclusive")
    p.add_argument("--handle", "-u", type=str, help="Your Codeforces handle to exclude solved problems")
    p.add_argument("--outdir", default="ladders", help="Output directory")
    p.add_argument("--sort", choices=["solved", "rating", "newest", "oldest"], default="solved")
    p.add_argument("--limit", type=int, default=0, help="Keep only top N after sort (0=no limit)")
    p.add_argument("--combine", action="store_true", help="Make one combined file instead of many per division+index")
    return p.parse_args()

def main():
    args = parse_args()
    exact_rating = args.rating
    min_rating = max_rating = None
    if args.range:
        min_rating, max_rating = args.range
        if min_rating > max_rating:
            print("Error: MIN cannot be greater than MAX", file=sys.stderr)
            sys.exit(1)

    print("Fetching contest list...")
    contest_map = fetch_contests()
    print("Fetching problems...")
    problems, solved_map = fetch_problemset()
    print(f"Total problems fetched: {len(problems)}")

    solved_set = set()
    if args.handle:
        print(f"Fetching solved problems for {args.handle}...")
        solved_set = fetch_solved_problems(args.handle)
        print(f"Total solved problems: {len(solved_set)}")

    rows = filter_and_annotate(
        problems=problems,
        solved_map=solved_map,
        contest_map=contest_map,
        wanted_divisions=args.divisions or [],
        wanted_indices=args.indices,
        exact_rating=exact_rating,
        min_rating=min_rating,
        max_rating=max_rating,
        solved_set=solved_set,
    )

    if not rows:
        print("No problems matched your filters.")
        return

    rows = sort_rows(rows, args.sort)
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    os.makedirs(args.outdir, exist_ok=True)

    def make_base_name(div: str, idx: str) -> str:
        if exact_rating is not None:
            return f"{div}_{idx}_rating_{exact_rating}"
        return f"{div}_{idx}_rating_{min_rating}-{max_rating}"

    if args.combine:
        title = "Codeforces Ladder — combined"
        csv_path = os.path.join(args.outdir, f"combined_ladder.csv")
        html_path = os.path.join(args.outdir, f"combined_ladder.html")
        write_csv(csv_path, rows)
        write_html(html_path, rows, title)
        print(f"Wrote combined CSV: {csv_path}")
        print(f"Wrote combined HTML: {html_path}")
        print(f"Problems: {len(rows)}")
        return

    groups: Dict[Tuple[str, str], List[dict]] = {}
    for r in rows:
        key = (r["division"], r["index"])
        groups.setdefault(key, []).append(r)

    total = 0
    for (div, idx), group_rows in groups.items():
        base = make_base_name(div, idx)
        csv_path = os.path.join(args.outdir, base + ".csv")
        html_path = os.path.join(args.outdir, base + ".html")
        write_csv(csv_path, group_rows)
        title = f"Codeforces Ladder — {div.upper()} {idx} " + (f"{exact_rating}" if exact_rating else f"{min_rating}-{max_rating}")
        write_html(html_path, group_rows, title)
        print(f"Wrote: {csv_path}  ({len(group_rows)} problems)")
        print(f"      {html_path}")
        total += len(group_rows)

    print(f"Total problems written: {total}")

if __name__ == "__main__":
    main()
