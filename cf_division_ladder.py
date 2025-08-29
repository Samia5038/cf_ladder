#!/usr/bin/env python3
"""
cf_division_ladder.py (API-friendly)
Fetch Codeforces problems, detect division, filter by index/rating,
exclude already solved problems, and return JSON ladder.
"""

import re
import requests
from typing import Dict, List, Tuple, Optional

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
    solved_map = {(s["contestId"], s["index"]): s.get("solvedCount", 0) for s in stats}
    return problems, solved_map

def fetch_solved_problems(handle: str) -> set:
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
            continue
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

# ---------------------- Sorting ----------------------

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

# ---------------------- Main API function ----------------------

def fetch_ladder(
    handle: Optional[str] = None,
    divisions: Optional[List[str]] = None,
    indices: Optional[List[str]] = None,
    exact_rating: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    sort_key: str = "solved"
) -> List[dict]:
    """
    Returns a list of unsolved problems filtered by rating/division/index.
    """
    contest_map = fetch_contests()
    problems, solved_map = fetch_problemset()
    solved_set = fetch_solved_problems(handle) if handle else set()

    rows = filter_and_annotate(
        problems=problems,
        solved_map=solved_map,
        contest_map=contest_map,
        wanted_divisions=divisions or [],
        wanted_indices=indices or ["A","B","C","D","E","F"],
        exact_rating=exact_rating,
        min_rating=min_rating,
        max_rating=max_rating,
        solved_set=solved_set
    )
    return sort_rows(rows, sort_key)
