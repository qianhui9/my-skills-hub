#!/usr/bin/env python3

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "sources" / "skills.json"


def run(cmd, cwd=None):
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def should_exclude(path: Path, exclude_names: list[str]) -> bool:
    parts = set(path.parts)
    return any(name in parts or path.name == name for name in exclude_names)


def copy_tree(src: Path, dst: Path, exclude: list[str]):
    if dst.exists():
        shutil.rmtree(dst)

    dst.mkdir(parents=True, exist_ok=True)

    for item in src.rglob("*"):
        rel = item.relative_to(src)

        if should_exclude(rel, exclude):
            continue

        target = dst / rel

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def sync_skill(skill: dict):
    name = skill["name"]

    if not skill.get("enabled", True):
        print(f"skip disabled skill: {name}")
        return

    repo = skill["repo"]
    ref = skill.get("ref", "main")
    source_subdir = skill.get("source_subdir", ".")
    target_dir = ROOT / skill["target_dir"]
    exclude = skill.get("exclude", [])

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / name

        run(["git", "clone", "--filter=blob:none", "--no-checkout", repo, str(tmp_path)])
        run(["git", "fetch", "--depth=1", "origin", ref], cwd=tmp_path)
        run(["git", "checkout", "FETCH_HEAD"], cwd=tmp_path)

        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=tmp_path,
            text=True
        ).strip()

        src = tmp_path / source_subdir
        if not src.exists():
            raise FileNotFoundError(f"{name}: source_subdir not found: {source_subdir}")

        copy_tree(src, target_dir, exclude)

        metadata = {
            "name": name,
            "repo": repo,
            "ref": ref,
            "commit": commit,
            "source_subdir": source_subdir
        }

        with open(target_dir / ".upstream.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            f.write("\n")

        print(f"synced {name} @ {commit}")


def main():
    with open(CONFIG, "r", encoding="utf-8-sig") as f:
        config = json.load(f)

    for skill in config.get("skills", []):
        sync_skill(skill)


if __name__ == "__main__":
    main()
