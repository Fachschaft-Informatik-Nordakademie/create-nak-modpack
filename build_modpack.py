#!/usr/bin/env python3
"""Baut CREATE-NAK-INF.mrpack + CREATE-NAK-INF-mods-manual.zip aus mods.txt.

Loest fuer jeden Slug in mods.txt (und rekursiv alle Pflichtabhaengigkeiten)
die neueste NeoForge/1.21.1-Version ueber die Modrinth-API auf, baut daraus
ein Modrinth-.mrpack (fuer Prism Launcher/Modrinth App/ATLauncher) sowie ein
flaches ZIP aller Client-Jars (fuer Lunar Client/manuelle Installation).
"""
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

MC_VERSION = "1.21.1"
LOADER = "neoforge"
API = "https://api.modrinth.com/v2"

# Reihenfolge = Reihenfolge der Ueberschriften in der README. Slugs, die hier
# nicht auftauchen (z.B. neu hinzugekommene Pflichtabhaengigkeiten), landen
# automatisch unter "Sonstige".
CATEGORIES = {
    "Create (Basis)": ["create"],
    "Create-Addons": [
        "createaddition", "create-structures-arise", "create-more-cogwheels",
        "create-utilities-(unofficial-port)", "create-steam-n-rails-1.21.1",
        "create-power-loader", "create-central-kitchen", "create-deco",
        "create-encased", "create-enchantment-industry", "create-integrated-farming",
        "create-liquid-fuel", "create-misc-and-things", "create-ore-excavation",
        "create-railways-navigator", "create-trading-floor", "create-trimmed",
        "hypertube", "interiors", "create-aeronautics",
        "create-copper-zinc", "create-framed", "create-goggles", "create-jetpack",
        "create-connected", "slice-and-dice", "create-dreams-and-desires", "escalated",
        "blocks-bogies", "create-propulsion-simulated", "create-threaded-trains",
        "create-factory", "create-mechanical-extruder",
    ],
    "Biomes O' Plenty": ["biomes-o-plenty", "createoplenty"],
    "Lagerung & Inventar": [
        "sophisticated-storage", "sophisticated-storage-create-integration",
        "sophisticated-backpacks", "sophisticated-backpacks-create-integration",
        "sophisticated-core", "sophisticated-jei-index",
    ],
    "Navigation & Teleport": [
        "waystones", "xaeros-minimap", "xaeros-world-map",
        "xaeros-minimap-world-map-waystones-compatibility-forge",
    ],
    "Performance": ["sodium", "lithium", "entityculling"],
    "Utility & QoL": ["jei", "veinminer", "simple-voice-chat"],
    "Bibliotheken (Pflichtabhängigkeiten)": [
        "balm", "dragonlib", "sable", "kotlin-lang-forge", "create-dragons-plus",
        "architectury-api", "glitchcore", "kotlin-for-forge", "mechanicals-lib", "terrablender",
    ],
}


def build_categorized_modlist_markdown(resolved: dict, titles: dict) -> str:
    seen = set()
    lines = []
    for cat, slugs in CATEGORIES.items():
        cat_slugs = [s for s in slugs if s in resolved]
        if not cat_slugs:
            continue
        seen.update(cat_slugs)
        lines.append(f"\n### {cat}\n")
        lines.append("| Mod | Version |")
        lines.append("|---|---|")
        for slug in cat_slugs:
            lines.append(f"| [{titles[slug]}](https://modrinth.com/mod/{slug}) | `{resolved[slug]['version_number']}` |")

    leftover = sorted(set(resolved) - seen)
    if leftover:
        lines.append("\n### Sonstige\n")
        lines.append("| Mod | Version |")
        lines.append("|---|---|")
        for slug in leftover:
            lines.append(f"| [{titles[slug]}](https://modrinth.com/mod/{slug}) | `{resolved[slug]['version_number']}` |")

    return "\n".join(lines) + "\n"


def update_readme_modlist(repo_dir: str, resolved: dict, sides: dict, titles: dict) -> None:
    readme_path = os.path.join(repo_dir, "README.md")
    content = open(readme_path).read()
    start_marker = "<!-- MODLIST:START -->"
    end_marker = "<!-- MODLIST:END -->"
    start = content.index(start_marker) + len(start_marker)
    end = content.index(end_marker)
    modlist = build_categorized_modlist_markdown(resolved, titles)
    content = content[:start] + "\n" + modlist + content[end:]
    open(readme_path, "w").write(content)


def fetch_versions(slug: str) -> list:
    q = urllib.parse.quote(slug, safe="")
    url = (
        f"{API}/project/{q}/version"
        f'?loaders=%5B%22{LOADER}%22%5D&game_versions=%5B%22{MC_VERSION}%22%5D'
    )
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def fetch_projects(slugs: list) -> list:
    if not slugs:
        return []
    ids = urllib.parse.quote(json.dumps(slugs))
    with urllib.request.urlopen(f"{API}/projects?ids={ids}") as r:
        return json.load(r)


def resolve_neoforge_version() -> str:
    with urllib.request.urlopen(
        "https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge"
    ) as r:
        data = json.load(r)
    versions = [v for v in data["versions"] if v.startswith("21.1.")]
    versions.sort(key=lambda v: tuple(int(p) for p in v.split(".")))
    return versions[-1]


def resolve_all(seed_slugs: list) -> dict:
    resolved = {}
    frontier = list(seed_slugs)
    seen = set()
    while frontier:
        slug = frontier.pop()
        if slug in seen:
            continue
        seen.add(slug)
        versions = fetch_versions(slug)
        if not versions:
            print(f"WARNING: no {LOADER}/{MC_VERSION} version for '{slug}', skipping", file=sys.stderr)
            continue
        v = versions[0]
        primary = next((f for f in v["files"] if f.get("primary")), v["files"][0])
        resolved[slug] = {
            "version_number": v["version_number"],
            "filename": primary["filename"],
            "url": primary["url"],
            "sha1": primary["hashes"]["sha1"],
            "sha512": primary["hashes"]["sha512"],
            "size": primary["size"],
        }
        req_ids = [
            d["project_id"]
            for d in v.get("dependencies", [])
            if d["dependency_type"] == "required" and d.get("project_id")
        ]
        if req_ids:
            for p in fetch_projects(req_ids):
                if p["slug"] not in resolved and p["slug"] not in seen:
                    frontier.append(p["slug"])
    return resolved


def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    seed_slugs = [
        line.split("#", 1)[0].strip()
        for line in open(os.path.join(repo_dir, "mods.txt"))
        if line.split("#", 1)[0].strip()
    ]

    print(f"Resolving {len(seed_slugs)} seed mods (+ dependencies) for {LOADER}/{MC_VERSION}...")
    resolved = resolve_all(seed_slugs)
    print(f"Resolved {len(resolved)} mods total.")

    projects = fetch_projects(list(resolved))
    sides = {p["slug"]: {"client": p["client_side"], "server": p["server_side"]} for p in projects}
    titles = {p["slug"]: p["title"] for p in projects}

    neoforge_version = resolve_neoforge_version()
    print(f"Latest NeoForge for {MC_VERSION}: {neoforge_version}")

    build_dir = os.path.join(repo_dir, "build")
    os.makedirs(os.path.join(build_dir, "overrides"), exist_ok=True)
    os.makedirs(os.path.join(build_dir, "lunar-mods"), exist_ok=True)

    files = []
    for slug, info in sorted(resolved.items()):
        side = sides[slug]
        files.append(
            {
                "path": f"mods/{info['filename']}",
                "hashes": {"sha1": info["sha1"], "sha512": info["sha512"]},
                "env": {"client": side["client"], "server": side["server"]},
                "downloads": [info["url"]],
                "fileSize": info["size"],
            }
        )

    mrpack = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": os.environ.get("MODPACK_VERSION", "dev"),
        "name": "CREATE@NAK-INF",
        "summary": "Create-Modpack der Fachschaft Informatik (NAK) — NeoForge 1.21.1.",
        "files": files,
        "dependencies": {"minecraft": MC_VERSION, "neoforge": neoforge_version},
    }

    index_path = os.path.join(build_dir, "modrinth.index.json")
    json.dump(mrpack, open(index_path, "w"), indent=2)

    mrpack_path = os.path.join(repo_dir, "CREATE-NAK-INF.mrpack")
    if os.path.exists(mrpack_path):
        os.remove(mrpack_path)
    os.system(
        f'cd "{build_dir}" && zip -q -r "{mrpack_path}" modrinth.index.json overrides'
    )
    print(f"Wrote {mrpack_path}")

    lunar_dir = os.path.join(build_dir, "lunar-mods")
    for slug, info in resolved.items():
        if sides[slug]["client"] == "unsupported":
            continue
        dest = os.path.join(lunar_dir, info["filename"])
        urllib.request.urlretrieve(info["url"], dest)
        h = hashlib.sha1(open(dest, "rb").read()).hexdigest()
        assert h == info["sha1"], f"sha1 mismatch for {slug}"

    readme = os.path.join(lunar_dir, "LIESMICH.txt")
    with open(readme, "w") as f:
        f.write(
            "CREATE@NAK-INF - Mods-Ordner (NeoForge {mc})\n"
            "================================================\n\n"
            "Fuer Lunar Client (eigenes NeoForge-{mc}-Profil noetig, NeoForge "
            "vorher separat installieren: https://neoforged.net, Version {nf}) "
            "oder jeden anderen NeoForge-{mc}-Client: kompletten Inhalt in den "
            "mods/-Ordner legen.\n\n"
            "Fuer Prism Launcher / Modrinth App / ATLauncher: stattdessen "
            "CREATE-NAK-INF.mrpack importieren.\n".format(mc=MC_VERSION, nf=neoforge_version)
        )

    zip_path = os.path.join(repo_dir, "CREATE-NAK-INF-mods-manual.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    os.system(f'cd "{lunar_dir}" && zip -q -r "{zip_path}" .')
    print(f"Wrote {zip_path}")

    update_readme_modlist(repo_dir, resolved, sides, titles)
    print("Updated README.md modlist section")

    print(f"NEOFORGE_VERSION={neoforge_version}")


if __name__ == "__main__":
    main()
