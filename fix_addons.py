#!/usr/bin/env python3
"""
fix_addons.py — Fix specific known issues in migrated rpext-index.json files,
then regenerate addons.json.

Issues fixed:
  1. virtio: broadwell* platforms incorrectly point to geminilake.json
             → corrected to recipes/broadwellnk.json
  2. powersched: all platforms point to releases/ds1019p_42218.json (old model_version)
                 → corrected to recipes/apollolake.json if it exists,
                   otherwise recipes/universal.json if it exists,
                   otherwise keep as-is with a warning
  3. Regenerates addons.json with all current platform keys

Usage:
  python3 fix_addons.py --addons /opt/tcrp/addons [--dry-run]
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

MV_RE = re.compile(r'^[a-z][a-z0-9]*_\d+$')

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"  ERROR reading {path}: {e}")
        return None

def save_json(path, data, dry_run):
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if dry_run:
        print(f"    [dry-run] would write {path.name}")
    else:
        bak = path.with_suffix(path.suffix + ".bak")
        if path.exists() and not bak.exists():
            shutil.copy2(path, bak)
        path.write_text(text)
        print(f"    wrote {path.name}")

def fix_virtio(addons_dir, dry_run):
    """Fix virtio: broadwell* incorrectly points to geminilake.json."""
    idx_file = addons_dir / "virtio" / "rpext-index.json"
    if not idx_file.exists():
        print("  virtio: not found — skipping")
        return

    idx      = load_json(idx_file)
    releases = idx.get("releases", {})
    base_url = "https://raw.githubusercontent.com/pocopico/trireme-addons/main/virtio/recipes/"

    broadwell_platforms = ["broadwell", "broadwellnk", "broadwellnkv2",
                           "broadwellntbap", "purley"]

    # Check recipes/broadwellnk.json exists locally
    bwnk_recipe = addons_dir / "virtio" / "recipes" / "broadwellnk.json"
    if not bwnk_recipe.exists():
        print(f"  virtio: WARNING — recipes/broadwellnk.json not found, skipping")
        return

    correct_url = base_url + "broadwellnk.json"
    changed = []
    for plat in broadwell_platforms:
        if plat in releases and releases[plat] != correct_url:
            releases[plat] = correct_url
            changed.append(plat)

    if changed:
        print(f"  virtio: fixing {changed} → broadwellnk.json")
        save_json(idx_file, {**idx, "releases": releases}, dry_run)
    else:
        print("  virtio: no broadwell platform issues found")

def fix_powersched(addons_dir, dry_run):
    """Fix powersched: all platforms point to old model_version descriptor."""
    idx_file = addons_dir / "powersched" / "rpext-index.json"
    if not idx_file.exists():
        print("  powersched: not found — skipping")
        return

    idx      = load_json(idx_file)
    releases = idx.get("releases", {})
    base_url = "https://raw.githubusercontent.com/pocopico/trireme-addons/main/powersched/"

    # Check what descriptor files exist
    recipes_dir  = addons_dir / "powersched" / "recipes"
    releases_dir = addons_dir / "powersched" / "releases"

    # Prefer: universal > apollolake > any existing platform descriptor
    candidate = None
    if (recipes_dir / "universal.json").exists():
        candidate = base_url + "recipes/universal.json"
        print(f"  powersched: using recipes/universal.json")
    elif (recipes_dir / "apollolake.json").exists():
        candidate = base_url + "recipes/apollolake.json"
        print(f"  powersched: using recipes/apollolake.json")
    elif releases_dir.exists():
        # Find any non-model_version .json
        for f in sorted(releases_dir.glob("*.json")):
            if not MV_RE.match(f.stem):
                candidate = base_url + f"releases/{f.name}"
                print(f"  powersched: using releases/{f.name}")
                break

    if not candidate:
        print("  powersched: WARNING — no suitable descriptor found, keeping as-is")
        return

    # Update all entries that currently point to a model_version file
    changed = []
    for plat, url in releases.items():
        fname = url.split("/")[-1].replace(".json", "")
        if MV_RE.match(fname):
            releases[plat] = candidate
            changed.append(plat)

    if changed:
        print(f"  powersched: fixing {len(changed)} entries → {candidate.split('/')[-1]}")
        save_json(idx_file, {**idx, "releases": releases}, dry_run)
    else:
        print("  powersched: no model_version entries found")

def regenerate_addons_json(addons_dir, dry_run):
    """Rebuild addons.json as NDJSON from all rpext-index.json files,
    including only platform keys (strip compat mv keys and zendofmodel)."""
    entries = []
    SENTINEL = "zendofmodel"
    for d in sorted(addons_dir.iterdir()):
        f = d / "rpext-index.json"
        if not d.is_dir() or not f.is_file():
            continue
        idx = load_json(f)
        if not (idx and idx.get("id") and idx.get("url")):
            continue
        # Strip model_version keys and sentinel from addons.json
        plat_only = {k: v for k, v in idx.get("releases", {}).items()
                     if k != SENTINEL and not MV_RE.match(k)}
        entries.append({**idx, "releases": plat_only})

    ndjson = "\n".join(json.dumps(e, separators=(",", ":")) for e in entries) + "\n"
    dst    = addons_dir / "addons.json"

    if dry_run:
        print(f"\n  [dry-run] would write addons.json ({len(entries)} entries)")
        # Show platform coverage for verification
        all_plats = set()
        for e in entries:
            all_plats.update(e.get("releases", {}).keys())
        print(f"  Platforms covered: {sorted(all_plats)}")
    else:
        bak = dst.with_suffix(".json.bak2")
        if dst.exists() and not bak.exists():
            shutil.copy2(dst, bak)
        dst.write_text(ndjson)
        print(f"\n  wrote addons.json ({len(entries)} entries)")

def main():
    ap = argparse.ArgumentParser(description="Fix known addon issues and regenerate addons.json")
    ap.add_argument("--addons",   required=True, help="Path to trireme-addons dir")
    ap.add_argument("--dry-run",  action="store_true")
    args = ap.parse_args()

    addons_dir = Path(args.addons)
    if not addons_dir.is_dir():
        print(f"ERROR: {addons_dir} not found"); sys.exit(1)

    dry = args.dry_run
    print(f"{'[DRY RUN] ' if dry else ''}Fixing addons in {addons_dir}\n")

    print("── virtio ──")
    fix_virtio(addons_dir, dry)
    print()

    print("── powersched ──")
    fix_powersched(addons_dir, dry)
    print()

    print("── addons.json ──")
    regenerate_addons_json(addons_dir, dry)
    print()
    print("Done.")

if __name__ == "__main__":
    main()
