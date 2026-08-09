import json
import os


def load_snapshot(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_snapshot(prev, current):
    result = {}
    for repo, stars in current.items():
        result[repo] = {"stars": stars, "delta": stars - prev.get(repo, stars)}
    for repo, stars in prev.items():
        if repo not in result:
            result[repo] = {"stars": stars, "delta": 0}
    return result
