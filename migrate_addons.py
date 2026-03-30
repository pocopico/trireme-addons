#!/usr/bin/env python3
"""
migrate_addons.py — Collapse rpext-index.json from model_version keys to platform keys.

THE INSIGHT
-----------
The release descriptor files are ALREADY named by platform:
  9p/releases/broadwellnk.json
  9p/releases/geminilake.json

Every model_version key already points to one of these URLs:
  "ds3622xsp_72806": ".../9p/releases/broadwellnk.json"  ← same url
  "ds3622xsp_69057": ".../9p/releases/broadwellnk.json"  ← same url
  "ds1621xsp_72806": ".../9p/releases/broadwellnk.json"  ← same url

Migration: extract platform name from URL value, use as key, deduplicate.
Release descriptor files are NOT touched.

BEFORE (100+ keys):           AFTER (one per platform):
  "ds3622xsp_72806": "...broadwellnk.json"    "broadwellnk": "...broadwellnk.json"
  "ds3622xsp_69057": "...broadwellnk.json"
  "ds1621xsp_72806": "...broadwellnk.json"

USAGE
-----
  python3 migrate_addons.py --addons /path/to/tcrp-addons --dry-run
  python3 migrate_addons.py --addons /path/to/tcrp-addons
  python3 migrate_addons.py --addons /path/to/tcrp-addons --no-compat
  python3 migrate_addons.py --addons /path/to/tcrp-addons --local-cache /opt/tcrp/addons
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def rewrite_urls(obj, old_repo: str, new_repo: str):
    """
    Recursively rewrite all GitHub URLs in a JSON object (dict/list/str)
    from old_repo to new_repo, normalising /master/ → /main/ along the way.
    Returns a new object with all strings replaced — original untouched.
    """
    if isinstance(obj, dict):
        return {k: rewrite_urls(v, old_repo, new_repo) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rewrite_urls(v, old_repo, new_repo) for v in obj]
    if isinstance(obj, str) and old_repo in obj:
        # Normalise master → main before repo rename
        url = obj.replace(f'/{old_repo}/master/', f'/{old_repo}/main/')
        url = url.replace(f'/{old_repo}/refs/heads/master/',
                          f'/{old_repo}/refs/heads/main/')
        return url.replace(old_repo, new_repo)
    return obj

MV_RE   = re.compile(r'^[a-z][a-z0-9]*_\d+$')   # model_version key: ds3622xsp_72806
PLAT_RE = re.compile(r'^[a-z][a-z0-9]+$')          # platform key:      broadwellnk
SENTINEL = "zendofmodel"

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"  ERROR reading {path}: {e}"); return None

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

def platform_from_url(url):
    """Extract platform name from release URL: .../releases/broadwellnk.json → broadwellnk"""
    m = re.search(r'/releases/([a-z][a-z0-9]+)\.json', url)
    return m.group(1) if m else ""

# Platform aliases — when an addon has no entry for a platform, use the
# closest equivalent.
#
# For NON-kernel-bound addons (no .ko / no kver in filenames): any platform
# alias is safe — the addon is pure userspace and ABI-independent.
#
# For KERNEL-BOUND addons (filenames contain kver like 4.4.302 or 5.10.55):
# only alias within the same kernel family.
#
# The script auto-detects kernel-bound status from the release descriptor.
# These dicts cover both cases; the script picks the right one.

# Same-kernel aliases (safe for kernel-bound AND userspace addons)
K4_ALIASES = {
    "broadwellnkv2":  "broadwellnk",   # broadwellnk v2 — same 4.4.x kernel
    "broadwellntbap": "broadwellnk",   # another broadwellnk derivative
    "purley":         "broadwellnk",   # Xeon broadwell-EP — same k4 arch
}
K5_ALIASES = {
    "geminilakenk":   "geminilake",    # geminilake nk — if k5 release exists
    "r1000nk":        "r1000",         # r1000 nk — if k5 release exists
    "v1000nk":        "v1000",         # v1000 nk — if k5 release exists
    "epyc7002":       "v1000",         # epyc7002 — closest AMD k5
}
# Cross-kernel aliases (ONLY safe for non-kernel-bound addons)
# Maps k5 missing platforms to their k4 nearest neighbour for userspace addons
CROSS_KERNEL_ALIASES = {
    "geminilakenk":   "geminilake",
    "r1000nk":        "r1000",
    "v1000nk":        "v1000",
    "epyc7002":       "v1000",
}

KVER_RE = re.compile(r'\d+\.\d+\.\d+')  # detects kernel version in filename

# All known platforms — used to expand platform-independent addons
ALL_PLATFORMS = [
    "apollolake", "broadwell", "broadwellnk", "broadwellnkv2", "broadwellntbap",
    "bromolow", "denverton", "epyc7002", "geminilake", "geminilakenk",
    "purley", "r1000", "r1000nk", "v1000", "v1000nk",
]

def migrate_one(idx_file, dry_run, compat, report, old_repo='', new_repo=''):
    idx = load_json(idx_file)
    if not idx:
        return False

    addon_id = idx.get("id", idx_file.parent.name)
    releases = idx.get("releases", {})
    if not releases:
        report.append(f"  {addon_id}: no releases — skipped"); return False

    mv_keys   = [k for k in releases if k != SENTINEL and MV_RE.match(k)]
    plat_keys = [k for k in releases if k != SENTINEL and PLAT_RE.match(k) and not MV_RE.match(k)]

    if not mv_keys:
        report.append(f"  {addon_id}: already migrated ({len(plat_keys)} platform keys) — skipped")
        return False

    # Build new platform-keyed releases from URL values
    new_releases = {}
    unmapped = []
    for mv_key, url in releases.items():
        if mv_key == SENTINEL: continue
        if not MV_RE.match(mv_key):          # already a platform key
            new_releases.setdefault(mv_key, url); continue
        plat = platform_from_url(url)
        if not plat:
            unmapped.append((mv_key, url)); continue
        new_releases.setdefault(plat, url)   # first occurrence wins

    # Handle platform-independent addons: all model_version keys point to
    # the same single URL that doesn't follow /releases/{platform}.json.
    # Expand to all known platforms so the addon appears for every user.
    if not new_releases and unmapped:
        canonical_url = unmapped[0][1]
        report.append(f"  {addon_id}: platform-independent — "
                      f"expanding to all {len(ALL_PLATFORMS)} platforms")
        print(f"  {addon_id}: platform-independent → expanding to "
              f"{len(ALL_PLATFORMS)} platforms")
        for plat in ALL_PLATFORMS:
            new_releases[plat] = canonical_url
        unmapped = []  # all accounted for
    elif unmapped and new_releases:
        # Partially mapped: some platforms have specific releases, others don't.
        # Fill gaps with the first unmapped URL (usually a generic/fallback).
        canonical_url = unmapped[0][1]
        gaps = [p for p in ALL_PLATFORMS if p not in new_releases]
        for plat in gaps:
            new_releases[plat] = canonical_url
        if gaps:
            report.append(f"  {addon_id}: filled {len(gaps)} gaps with "
                          f"generic URL {canonical_url.split('/')[-1]}")
        unmapped = []  # consumed

    # Detect whether this addon is kernel-bound by checking for kver
    # patterns (e.g. "4.4.302", "5.10.55") in any release descriptor filename.
    # We sample the first available release descriptor URL to check.
    kernel_bound = False
    sample_url = next(iter(new_releases.values()), "")
    if sample_url:
        # Fetch the descriptor to check filenames — use local file if possible
        sample_file = idx_file.parent / "releases" / sample_url.split("/releases/")[-1]
        if sample_file.exists():
            try:
                desc = load_json(sample_file)
                if desc:
                    for f in desc.get("files", []):
                        if KVER_RE.search(f.get("name", "")):
                            kernel_bound = True; break
            except Exception:
                pass

    # Apply platform aliases
    # k4 aliases are always safe (same kernel family)
    # k5 aliases: safe if k5 release exists; for non-kernel addons use cross-kernel too
    aliases_added = []
    all_aliases = {**K4_ALIASES}
    if not kernel_bound:
        # Userspace addon: cross-kernel aliasing is safe — ABI-independent
        all_aliases.update(CROSS_KERNEL_ALIASES)
    else:
        # Kernel-bound addon: only add k5 aliases when the source platform's
        # release descriptor actually contains a k5 filename (5.x.x kver).
        # A geminilake entry with "geminilake-4.4.180.tgz" must NOT be used
        # for geminilakenk (k5 kernel) — wrong ABI.
        for k5_plat, src_plat in K5_ALIASES.items():
            if src_plat not in new_releases:
                continue
            src_url = new_releases[src_plat]
            src_desc = idx_file.parent / "releases" / src_url.split("/releases/")[-1]
            if src_desc.exists():
                try:
                    desc = load_json(src_desc)
                    files = [f.get("name","") for f in (desc or {}).get("files",[])]
                    # Only alias if source has a 5.x.x filename (actual k5 build)
                    if any(re.search(r'5\.\d+\.\d+', f) for f in files):
                        all_aliases[k5_plat] = src_plat
                except Exception:
                    pass

    for alias_plat, source_plat in all_aliases.items():
        if alias_plat not in new_releases and source_plat in new_releases:
            new_releases[alias_plat] = new_releases[source_plat]
            aliases_added.append(f"{alias_plat}→{source_plat}")

    k5_missing = [p for p in (K5_ALIASES if kernel_bound else {})
                  if p not in new_releases]

    # Compat: keep old mv keys pointing to same url
    compat_entries = {}
    if compat:
        for mv_key, url in releases.items():
            if mv_key != SENTINEL and MV_RE.match(mv_key):
                compat_entries[mv_key] = url

    final = {**new_releases, **compat_entries}

    summary = (f"  {addon_id}: {len(mv_keys)} mv keys → {len(new_releases)} platform keys"
               + (f" + {len(compat_entries)} compat shims" if compat and compat_entries else "")
               + (f"  [{len(unmapped)} unmapped]" if unmapped else ""))
    report.append(summary)
    print(summary)
    for plat, url in sorted(new_releases.items()):
        all_alias_map = {**K4_ALIASES, **CROSS_KERNEL_ALIASES}
        src = f" (alias of {all_alias_map[plat]})" if plat in all_alias_map else ""
        report.append(f"    {plat:20s} → {url.split('/')[-1]}{src}")
    if aliases_added:
        report.append(f"    k4 aliases added: {', '.join(aliases_added)}")
    if k5_missing:
        report.append(f"    k5 no coverage (correct): {', '.join(k5_missing)}")
    if unmapped:
        report.append("    UNMAPPED:"); [report.append(f"      {k}: {u}") for k, u in unmapped[:5]]

    new_idx = {**idx, "releases": final}
    if new_repo:
        new_idx = rewrite_urls(new_idx, old_repo, new_repo)
        report.append(f"    URLs rewritten: {old_repo} → {new_repo}")
    save_json(idx_file, new_idx, dry_run)
    return True

def rewrite_release_descriptors(addons_dir, old_repo, new_repo, dry_run, report):
    """Rewrite URLs in ALL JSON files under each addon dir (recursive).
    Covers releases/{platform}.json, {addon}.json at root, and any other
    descriptor files regardless of location.
    Skips rpext-index.json — that is already handled by migrate_one.
    """
    if not new_repo:
        return
    count = 0
    for d in sorted(addons_dir.iterdir()):
        if not d.is_dir(): continue
        for f in sorted(d.rglob('*.json')):
            if f.name == 'rpext-index.json': continue  # already rewritten
            desc = load_json(f)
            if not desc: continue
            new_desc = rewrite_urls(desc, old_repo, new_repo)
            if new_desc != desc:
                save_json(f, new_desc, dry_run)
                count += 1
    report.append(f"  descriptor files rewritten: {count}")
    print(f"  rewrote URLs in {count} descriptor file(s)")


def regenerate_addons_json(addons_dir, dry_run, report):
    entries = []
    for d in sorted(addons_dir.iterdir()):
        f = d / "rpext-index.json"
        if not d.is_dir() or not f.is_file(): continue
        idx = load_json(f)
        if not (idx and idx.get("id") and idx.get("url")): continue
        # addons.json only contains platform keys — strip compat mv keys
        plat_only = {k: v for k, v in idx.get("releases", {}).items()
                     if k != SENTINEL and not MV_RE.match(k)}
        entries.append({**idx, "releases": plat_only})

    ndjson = "\n".join(json.dumps(e, separators=(",", ":")) for e in entries) + "\n"
    dst = addons_dir / "addons.json"
    report.append(f"  addons.json: {len(entries)} entries")
    if dry_run:
        print(f"  [dry-run] would write addons.json ({len(entries)} entries)")
    else:
        bak = dst.with_suffix(".json.bak")
        if dst.exists() and not bak.exists(): shutil.copy2(dst, bak)
        dst.write_text(ndjson)
        print(f"  wrote addons.json ({len(entries)} entries)")

def sync_cache(addons_dir, cache_dir, dry_run, report):
    report.append(f"  cache: {cache_dir}")
    if dry_run: print(f"  [dry-run] would sync to {cache_dir}"); return
    cache_dir.mkdir(parents=True, exist_ok=True)
    src = addons_dir / "addons.json"
    if src.exists(): shutil.copy2(src, cache_dir / "addons.json")
    count = 0
    for d in sorted(addons_dir.iterdir()):
        f = d / "rpext-index.json"
        if not d.is_dir() or not f.is_file(): continue
        (cache_dir / d.name).mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, cache_dir / d.name / "rpext-index.json")
        count += 1
    print(f"  synced {count} addon index files to {cache_dir}")

def rewrite_config_jsons(config_dir: Path, old_repo: str, new_repo: str,
                         dry_run: bool, report: list):
    """
    Rewrite add_extensions URLs in all platform config.json files.
    Walks config_dir recursively and rewrites any URL referencing old_repo.
    """
    if not new_repo:
        return
    count = 0
    for f in sorted(config_dir.rglob("config.json")):
        data = load_json(f)
        if not data: continue
        new_data = rewrite_urls(data, old_repo, new_repo)
        if new_data != data:
            save_json(f, new_data, dry_run)
            count += 1
    report.append(f"  config.json files rewritten: {count}")
    print(f"  rewrote add_extensions URLs in {count} config.json file(s)")


def main():
    ap = argparse.ArgumentParser(description="Migrate tcrp-addons to platform keys")
    ap.add_argument("--addons",      required=True)
    ap.add_argument("--local-cache", default="")
    ap.add_argument("--no-compat",   action="store_true",
                    help="Remove legacy model_version keys (default: keep as shims)")
    ap.add_argument("--old-repo",    default="pocopico/tcrp-addons",
                    help="GitHub owner/repo to rewrite from (default: pocopico/tcrp-addons)")
    ap.add_argument("--new-repo",    default="",
                    help="GitHub owner/repo to rewrite to (e.g. pocopico/trireme-addons). "
                         "Omit to skip URL rewriting.")
    ap.add_argument("--config-dir",  default="",
                    help="Path to platform config dir (e.g. /opt/tcrp/config). "
                         "Rewrites add_extensions URLs in all config.json files.")
    ap.add_argument("--dry-run",     action="store_true")
    ap.add_argument("--report",      default="migrate_addons_report.txt")
    args = ap.parse_args()

    addons_dir = Path(args.addons)
    if not addons_dir.is_dir():
        print(f"ERROR: {addons_dir} not found"); sys.exit(1)

    compat  = not args.no_compat
    dry_run = args.dry_run

    print(f"{'[DRY RUN] ' if dry_run else ''}Migrating: {addons_dir}")
    print(f"Compat shims: {'yes' if compat else 'no'}")
    print()

    addon_dirs = sorted(d for d in addons_dir.iterdir()
                        if d.is_dir() and (d / "rpext-index.json").exists())
    if not addon_dirs:
        print("No addons found."); sys.exit(1)
    print(f"Found {len(addon_dirs)} addon(s)\n")

    report = ["migrate_addons report", "=" * 60,
              f"dir: {addons_dir}", f"compat: {compat}", ""]
    migrated = 0
    old_repo = args.old_repo
    new_repo = args.new_repo
    if new_repo:
        print(f"URL rewrite: {old_repo} → {new_repo}")
        print()

    for d in addon_dirs:
        print(f"── {d.name} ──")
        report.append(f"[{d.name}]")
        if migrate_one(d / "rpext-index.json", dry_run, compat, report,
                       old_repo=old_repo, new_repo=new_repo):
            migrated += 1
        report.append(""); print()

    # Rewrite URLs in release descriptor files (platform.json)
    if new_repo:
        print("── rewriting release descriptor URLs ──")
        rewrite_release_descriptors(addons_dir, old_repo, new_repo, dry_run, report)
        print()

    # Rewrite add_extensions URLs in platform config.json files
    if args.config_dir:
        config_dir = Path(args.config_dir)
        if config_dir.is_dir():
            print("── rewriting config.json add_extensions URLs ──")
            rewrite_config_jsons(config_dir, old_repo, new_repo, dry_run, report)
            print()
        else:
            print(f"WARNING: --config-dir {config_dir} not found — skipping")

    print("── addons.json ──")
    regenerate_addons_json(addons_dir, dry_run, report)
    print()

    if args.local_cache:
        print(f"── sync cache ──")
        sync_cache(addons_dir, Path(args.local_cache), dry_run, report)
        print()

    report += ["", "=" * 60, f"Migrated: {migrated}/{len(addon_dirs)}",
               "", "Next steps:",
               "  1. Verify .bak files, check releases dict",
               "  2. Commit updated trireme-addons repo",
               "  3. Update ADDONS_URL in api.js to point to new repo",
               "  4. Update extmgr.sh: pass platform name to extvars()",
               "  4. Update api.js getPlatform(): use platforms.json lookup",
               "  5. Update build.js addExtensions(): pass platform name",
               "  6. When all devices updated: re-run with --no-compat"]

    if not dry_run:
        Path(args.report).write_text("\n".join(report) + "\n")
        print(f"Report: {args.report}")
    else:
        print("\n── Report ──"); print("\n".join(report))

    print(f"\n{'Dry run complete.' if dry_run else 'Done.'}")

if __name__ == "__main__":
    main()