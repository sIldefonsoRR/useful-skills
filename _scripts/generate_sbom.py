#!/usr/bin/env python3
"""Generate sbom.cdx.json (CycloneDX 1.6) for this repository.

Every top-level folder containing a SKILL.md is listed as a component, with
each tracked file in it hashed (SHA-256). Run after changing any skill file:

    python3 _scripts/generate_sbom.py

Uses only the Python standard library and git.
"""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import uuid

REPO = "sIldefonsoRR/useful-skills"
LICENSE = [{"license": {"id": "MIT"}}]
ROOT = pathlib.Path(__file__).resolve().parent.parent


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def skill_component(skill, files, sha):
    md = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
    desc = re.search(r"^description:\s*(.+)$", md, re.M).group(1).strip()
    return {
        "type": "application",
        "bom-ref": f"skill:{skill}",
        "name": skill,
        "version": sha[:7],
        "description": desc,
        "licenses": LICENSE,
        "purl": f"pkg:github/{REPO}@{sha}#{skill}",
        "components": [
            {
                "type": "file",
                "bom-ref": f,
                "name": f,
                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256((ROOT / f).read_bytes()).hexdigest()}],
            }
            for f in files
        ],
        "properties": [
            {"name": "skill:format", "value": "Agent Skills (SKILL.md)"},
            {"name": "skill:runtime-requirements", "value": "git, grep, date (host-provided, not bundled)"},
        ],
    }


def main():
    sha = git("rev-parse", "HEAD")
    tracked = git("ls-files").splitlines()
    skills = sorted({f.split("/")[0] for f in tracked if f.count("/") == 1 and f.endswith("/SKILL.md")})
    components = [
        skill_component(s, sorted(f for f in tracked if f.startswith(s + "/")), sha) for s in skills
    ]
    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": {
                "type": "application",
                "bom-ref": "useful-skills",
                "name": "useful-skills",
                "version": sha[:7],
                "purl": f"pkg:github/{REPO}@{sha}",
                "licenses": LICENSE,
                "externalReferences": [{"type": "vcs", "url": f"https://github.com/{REPO}"}],
            },
        },
        "components": components,
        "dependencies": [{"ref": "useful-skills", "dependsOn": [c["bom-ref"] for c in components]}]
        + [{"ref": c["bom-ref"], "dependsOn": []} for c in components],
    }
    out = ROOT / "sbom.cdx.json"
    out.write_text(json.dumps(bom, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}: {len(components)} skills, "
          f"{sum(len(c['components']) for c in components)} files")


if __name__ == "__main__":
    main()
