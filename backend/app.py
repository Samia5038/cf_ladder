# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import requests, re

# app = Flask(__name__)
# CORS(app)

# PROBLEMS_URL = "https://codeforces.com/api/problemset.problems"
# CONTESTS_URL = "https://codeforces.com/api/contest.list"
# USER_SUBMISSIONS_URL = "https://codeforces.com/api/user.status"

# def fetch_contests():
#     r = requests.get(CONTESTS_URL, params={"gym": False}, timeout=60)
#     r.raise_for_status()
#     data = r.json()
#     if data.get("status") != "OK":
#         raise RuntimeError("Failed to fetch contests")
#     return {c["id"]: c.get("name", "") for c in data["result"]}

# def fetch_problemset():
#     r = requests.get(PROBLEMS_URL, timeout=60)
#     r.raise_for_status()
#     data = r.json()
#     if data.get("status") != "OK":
#         raise RuntimeError("Failed to fetch problems")
#     problems = data["result"]["problems"]
#     stats = data["result"].get("problemStatistics", [])
#     solved_map = {(s["contestId"], s["index"]): s.get("solvedCount", 0) for s in stats}
#     return problems, solved_map

# def fetch_solved_problems(handle: str):
#     url = f"{USER_SUBMISSIONS_URL}?handle={handle}"
#     r = requests.get(url, timeout=60)
#     r.raise_for_status()
#     data = r.json()
#     solved = set()
#     if data.get("status") != "OK":
#         return solved
#     for sub in data["result"]:
#         if sub.get("verdict") == "OK":
#             pid = sub.get("problem", {})
#             solved.add((pid.get("contestId"), pid.get("index")))
#     return solved

# def detect_division_from_contest_name(name: str):
#     if not name:
#         return None
#     m = re.search(r"div(?:\.|\s)?\s*([1-4])", name, flags=re.I)
#     if m: return f"div{m.group(1)}"
#     m2 = re.search(r"division\s*([1-4])", name, flags=re.I)
#     if m2: return f"div{m2.group(1)}"
#     return None

# def filter_problems(problems, solved_map, contest_map, solved_set, min_rating, max_rating):
#     rows = []
#     for p in problems:
#         r = p.get("rating")
#         if r is None or r < min_rating or r > max_rating:
#             continue
#         cid = p.get("contestId")
#         idx = p.get("index")
#         if solved_set and (cid, idx) in solved_set:
#             continue
#         contest_name = contest_map.get(cid, "")
#         division = detect_division_from_contest_name(contest_name) or "unknown"
#         sc = solved_map.get((cid, idx), 0)
#         link = f"https://codeforces.com/contest/{cid}/problem/{idx}"
#         rows.append({
#             "contestId": cid,
#             "contestName": contest_name,
#             "index": idx,
#             "name": p.get("name", ""),
#             "rating": r,
#             "tags": p.get("tags", []),
#             "solvedCount": sc,
#             "link": link,
#             "division": division,
#         })
#     return rows

# def sort_rows(rows, sort_key):
#     if sort_key == "solved":
#         return sorted(rows, key=lambda x: (-x["solvedCount"], x["rating"], x["contestId"], x["index"]))
#     if sort_key == "rating":
#         return sorted(rows, key=lambda x: (x["rating"], x["contestId"], x["index"]))
#     if sort_key == "newest":
#         return sorted(rows, key=lambda x: (-x["contestId"], x["index"]))
#     if sort_key == "oldest":
#         return sorted(rows, key=lambda x: (x["contestId"], x["index"]))
#     return rows

# @app.route("/api/ladder")
# def ladder():
#     handle = request.args.get("handle", "Samia5038")
#     min_rating = int(request.args.get("min", 800))
#     max_rating = int(request.args.get("max", 3500))
#     sort_key = request.args.get("sort", "solved")

#     try:
#         contest_map = fetch_contests()
#         print(f"Contests fetched: {len(contest_map)}")
#         problems, solved_map = fetch_problemset()
#         print(f"Problems fetched: {len(problems)}")
#         solved_set = fetch_solved_problems(handle)
#         print(f"Solved fetched for {handle}: {len(solved_set)}")
#         rows = filter_problems(problems, solved_map, contest_map, solved_set, min_rating, max_rating)
#         print(f"Filtered problems: {len(rows)}")
#         rows = sort_rows(rows, sort_key)
#         return jsonify(rows)
#     except Exception as e:
#         print("Error:", e)
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)







# #!/usr/bin/env python3
# # backend/app.py
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import requests, re

# app = Flask(__name__)
# CORS(app)

# PROBLEMS_URL = "https://codeforces.com/api/problemset.problems"
# CONTESTS_URL = "https://codeforces.com/api/contest.list"
# USER_SUBMISSIONS_URL = "https://codeforces.com/api/user.status"

# def fetch_contests():
#     r = requests.get(CONTESTS_URL, params={"gym": False}, timeout=60)
#     r.raise_for_status()
#     data = r.json()
#     if data.get("status") != "OK":
#         raise RuntimeError("Failed to fetch contests")
#     return {c["id"]: c.get("name", "") for c in data["result"]}

# def fetch_problemset():
#     r = requests.get(PROBLEMS_URL, timeout=60)
#     r.raise_for_status()
#     data = r.json()
#     if data.get("status") != "OK":
#         raise RuntimeError("Failed to fetch problems")
#     problems = data["result"]["problems"]
#     stats = data["result"].get("problemStatistics", [])
#     solved_map = {(s["contestId"], s["index"]): s.get("solvedCount", 0) for s in stats}
#     return problems, solved_map

# def fetch_solved_problems(handle: str):
#     if not handle:
#         return set()
#     r = requests.get(f"{USER_SUBMISSIONS_URL}?handle={handle}", timeout=60)
#     r.raise_for_status()
#     data = r.json()
#     solved = set()
#     if data.get("status") != "OK":
#         return solved
#     for sub in data["result"]:
#         if sub.get("verdict") == "OK":
#             pid = sub.get("problem", {})
#             solved.add((pid.get("contestId"), pid.get("index")))
#     return solved

# _div_re = re.compile(r"div(?:\.|\s)?\s*([1-4])", flags=re.I)
# def detect_division_from_contest_name(name: str):
#     if not name: return None
#     m = _div_re.search(name)
#     if m: return f"div{m.group(1)}"
#     m2 = re.search(r"division\s*([1-4])", name, flags=re.I)
#     if m2: return f"div{m2.group(1)}"
#     return "unknown"

# def filter_and_prepare(problems, solved_map, contest_map, solved_set, min_rating, max_rating, wanted_indices):
#     wanted_indices = [x.upper() for x in (wanted_indices or [])]
#     rows = []
#     for p in problems:
#         r = p.get("rating")
#         if r is None or r < min_rating or r > max_rating:
#             continue
#         idx = p.get("index", "")
#         if wanted_indices and idx.upper() not in wanted_indices:
#             continue
#         cid = p.get("contestId")
#         if solved_set and (cid, idx) in solved_set:
#             continue
#         contest_name = contest_map.get(cid, "")
#         division = detect_division_from_contest_name(contest_name)
#         rows.append({
#             "contestId": cid,
#             "contestName": contest_name,
#             "index": idx,
#             "name": p.get("name", ""),
#             "rating": r,
#             "tags": p.get("tags", []),
#             "solvedCount": solved_map.get((cid, idx), 0),
#             "link": f"https://codeforces.com/contest/{cid}/problem/{idx}",
#             "division": division
#         })
#     return rows

# def sort_rows(rows, key):
#     if key == "solved": return sorted(rows, key=lambda x: (-x["solvedCount"], x["rating"]))
#     if key == "rating": return sorted(rows, key=lambda x: (x["rating"], x["contestId"]))
#     if key == "newest": return sorted(rows, key=lambda x: (-x["contestId"]))
#     if key == "oldest": return sorted(rows, key=lambda x: (x["contestId"]))
#     return rows

# @app.route("/api/ladder")
# def ladder():
#     try:
#         handle = request.args.get("handle", "")
#         min_rating = int(request.args.get("min", 800))
#         max_rating = int(request.args.get("max", 3500))
#         sort_key = request.args.get("sort", "solved")
#         indices_param = request.args.get("indices", "")  # "A,B,C"
#         wanted_indices = indices_param.split(",") if indices_param else []

#         contest_map = fetch_contests()
#         problems, solved_map = fetch_problemset()
#         solved_set = fetch_solved_problems(handle)
#         rows = filter_and_prepare(problems, solved_map, contest_map, solved_set, min_rating, max_rating, wanted_indices)
#         rows = sort_rows(rows, sort_key)
#         return jsonify(rows)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)



#!/usr/bin/env python3
# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, re

app = Flask(__name__)
CORS(app)

PROBLEMS_URL = "https://codeforces.com/api/problemset.problems"
CONTESTS_URL = "https://codeforces.com/api/contest.list"
USER_SUBMISSIONS_URL = "https://codeforces.com/api/user.status"

_div_re = re.compile(r"div(?:\.|\s)?\s*([1-4])", flags=re.I)

def fetch_contests():
    r = requests.get(CONTESTS_URL, params={"gym": False}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        raise RuntimeError("Failed to fetch contests")
    return {c["id"]: c.get("name", "") for c in data["result"]}

def fetch_problemset():
    r = requests.get(PROBLEMS_URL, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        raise RuntimeError("Failed to fetch problems")
    problems = data["result"]["problems"]
    stats = data["result"].get("problemStatistics", [])
    solved_map = {(s["contestId"], s["index"]): s.get("solvedCount", 0) for s in stats}
    return problems, solved_map

def fetch_solved_problems(handle: str):
    if not handle:
        return set()
    r = requests.get(f"{USER_SUBMISSIONS_URL}?handle={handle}", timeout=60)
    r.raise_for_status()
    data = r.json()
    solved = set()
    if data.get("status") != "OK":
        return solved
    for sub in data["result"]:
        if sub.get("verdict") == "OK":
            pid = sub.get("problem", {})
            solved.add((pid.get("contestId"), pid.get("index")))
    return solved

def detect_division_from_contest_name(name: str):
    if not name: return "unknown"
    m = _div_re.search(name)
    if m: return f"div{m.group(1)}"
    m2 = re.search(r"division\s*([1-4])", name, flags=re.I)
    if m2: return f"div{m2.group(1)}"
    return "unknown"

def filter_and_prepare(problems, solved_map, contest_map, solved_set, min_rating, max_rating, wanted_indices):
    wanted_indices = [x.upper() for x in (wanted_indices or [])]
    rows = []
    for p in problems:
        r = p.get("rating")
        if r is None or r < min_rating or r > max_rating:
            continue
        idx = p.get("index", "")
        if wanted_indices and idx.upper() not in wanted_indices:
            continue
        cid = p.get("contestId")
        contest_name = contest_map.get(cid, "")
        division = detect_division_from_contest_name(contest_name)
        is_solved = (cid, idx) in solved_set if solved_set else False
        rows.append({
            "contestId": cid,
            "contestName": contest_name,
            "index": idx,
            "name": p.get("name", ""),
            "rating": r,
            "tags": p.get("tags", []),
            "solvedCount": solved_map.get((cid, idx), 0),
            "link": f"https://codeforces.com/contest/{cid}/problem/{idx}",
            "division": division,
            "solved": is_solved   # 👈 added field
        })
    return rows


def sort_rows(rows, key):
    if key == "solved": return sorted(rows, key=lambda x: (-x["solvedCount"], x["rating"], x["contestId"], x["index"]))
    if key == "rating": return sorted(rows, key=lambda x: (x["rating"], x["contestId"], x["index"]))
    if key == "newest": return sorted(rows, key=lambda x: (-x["contestId"], x["index"]))
    if key == "oldest": return sorted(rows, key=lambda x: (x["contestId"], x["index"]))
    return rows

@app.route("/api/ladder")
def ladder():
    try:
        handle = request.args.get("handle", "").strip()
        min_rating = int(request.args.get("min", 800))
        max_rating = int(request.args.get("max", 3500))
        sort_key = request.args.get("sort", "solved")
        indices_param = request.args.get("indices", "").strip()  # e.g. "A,B"
        wanted_indices = [x.strip() for x in indices_param.split(",") if x.strip()] if indices_param else []

        contest_map = fetch_contests()
        problems, solved_map = fetch_problemset()
        solved_set = fetch_solved_problems(handle)
        rows = filter_and_prepare(problems, solved_map, contest_map, solved_set, min_rating, max_rating, wanted_indices)
        rows = sort_rows(rows, sort_key)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def health():
    return jsonify({"status":"ok","note":"/api/ladder available"}), 200

if __name__ == "__main__":
    app.run(debug=True)
