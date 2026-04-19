"""
take_snapshot.py – Fetch the current list of low-code tools from GitHub and
save it as a dated snapshot CSV in the snapshots/ folder.

Usage:
    python take_snapshot.py

The output file is named snapshot-YYYY-MM-DD.csv using today's date and is
written to the snapshots/ directory. The CSV format matches the existing
snapshot files (same columns, same ordering).
"""

import os
import sys
import requests
from datetime import datetime, timedelta
import snapshot_utils

GITHUB_API_URL = "https://api.github.com/search/repositories"

EXCLUDED_REPOS = {
    "JeecgBoot", "supervision", "amis", "APIJSON", "awesome-lowcode", "LoRA", "activepieces",
    "gop", "pycaret", "viztracer", "joint", "mometa", "asmjit", "NullAway",
    "self-hosted-ai-starter-kit", "sparrow", "smart-admin", "tracecat", "dooringx",
    "Genie.jl", "instill-core", "metarank", "dataprep", "hyperlight", "go-streams",
    "dashpress", "lowcode-demo", "diboot", "steedos-platform", "opsli-boot",
    "PiML-Toolbox", "marsview", "openDataV",
    "Awesome-CVPR2024-CVPR2021-CVPR2020-Low-Level-Vision", "dart_native",
    "low-level-programming", "vue-component-creater-ui", "ovine", "vlife", "beelzebub",
    "mtbird", "Awesome-CVPR2024-Low-Level-Vision", "create-chart", "crusher",
    "yuzi-generator", "pc-Dooring", "citrus", "Conduit", "react-admin-firebase",
    "apex", "fire-hpp", "awesome-lowcode", "karamel", "flowpipe", "fast-trade", "pd",
    "MetaLowCode", "vue-low-code", "css-text-portrait-builder", "awesome-low-code",
    "langwatch", "web-builder", "awesome-nocode-lowcode", "LLFlow", "AS-Editor",
    "mfish-nocode", "naas", "Awesome-ECCV2024-ECCV2020-Low-Level-Vision", "dataCompare",
    "AIVoiceChat", "illa", "praxis-ide", "low-level-design", "HuggingFists", "dagr",
    "pddon-win", "all-classification-templetes-for-ML", "node-red-dashboard", "Palu"
    "Liuma-platform", "crudapi-admin-web", "Awesome-ICCV2023-Low-Level-Vision", "pocketblocks"
    "plugins", "LLFormer", "vue-admin", "Low-Code", "FTC-Skystone-Dark-Angels-Romania-2020",
    "WrldTmpl8", "daas-start-kit", "Meta3D", "css-selector-tool", "corebos", "wave-apps",
    "self-hosted", "Automation-workflow", "banglanmt", "Nalu", "no-code-architects-toolkit",
    "MasteringMCU2", "Liuma-engine", "lowcode-tools", "Diff-Plugin", "mfish-nocode-view",
    "backroad", "zcbor", "powerfx-samples", "MemoryNet", "igop", "underTheHoodOfExecutables",
    "StringReloads", "lowcode-b", "EigenTrajectory", "pluto", "pixiebrix-extension", "dozer",
    "vite-vue3-lowcode",
    "qLDPC", "Visio", "Hack-SQL", "cow-Low-code", "LoRA-Pro", "OTE-GAN", "opsli-ui", "three-editor",
    "lowcode-code-generator-demo", "QuadPrior", "UIGO", "SoRA", "grid-form", "CcView", "verus",
    "fastgraphml", "arcane.cpp", "lowcode-engine-ext", "Liuma-platform", "lowcode-plugins", "turbo",
    "DegAE_DegradationAutoencoder", "www-project-top-10-low-code-no-code-security-risks", "lowcode-materials",
    "Vibration-Based-Fault-Diagnosis-with-Low-Delay", "alignment-attribution-code", "VideoUIKit-Web-React",
    "ReGitLint", "pandas-gpt", "yao-knowledge", "snac", "relora", "mettle", "Tenon",
    "noncode-projects-2024", "EvLight",
}


def fetch_repos(query="low-code", sort="stars", order="desc", per_page=100, max_pages=10):
    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    full_query = f"{query} stars:>=50 pushed:>={cutoff}"
    all_repos = []

    for page in range(1, max_pages + 1):
        params = {"q": full_query, "sort": sort, "order": order,
                  "per_page": per_page, "page": page}
        try:
            response = requests.get(GITHUB_API_URL, params=params, timeout=15)
            response.raise_for_status()
            items = response.json().get("items", [])
            if not items:
                break
            all_repos.extend(items)
            print(f"  page {page}: +{len(items)} repos (total {len(all_repos)})")
        except requests.exceptions.RequestException as e:
            print(f"  ERROR on page {page}: {e}", file=sys.stderr)
            break

    return all_repos


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(snapshot_utils.SNAPSHOTS_DIR, f"snapshot-{today}.csv")

    if os.path.exists(output_path):
        print(f"Snapshot for today already exists: {output_path}")
        print("Delete it first if you want to regenerate.")
        sys.exit(0)

    print("Fetching repos from GitHub API...")
    repos = fetch_repos()
    print(f"Fetched {len(repos)} repos total")

    filtered = [r for r in repos if r["name"] not in EXCLUDED_REPOS]
    count = snapshot_utils.repos_to_csv(filtered, output_path)
    print(f"After exclusions: {count} repos")
    print(f"Snapshot saved: {output_path}")


if __name__ == "__main__":
    main()
