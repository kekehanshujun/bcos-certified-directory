from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "projects.json"
DIST = ROOT / "dist"
OUT = DIST / "index.html"

TIERS = {"L0", "L1", "L2"}
CATEGORIES = {"agent-infra", "video", "blockchain", "compute-rentals", "tooling"}
SBOM_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_projects() -> list[dict]:
    projects = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(projects, list):
        raise ValueError("data/projects.json must contain a list")

    seen = set()
    for item in projects:
        missing = {
            "id",
            "name",
            "url",
            "github",
            "category",
            "bcos_tier",
            "latest_attested_sha",
            "sbom_hash",
            "review_note",
        } - set(item)
        if missing:
            raise ValueError(f"{item.get('id', '<unknown>')} missing fields: {sorted(missing)}")
        if item["id"] in seen:
            raise ValueError(f"duplicate project id: {item['id']}")
        seen.add(item["id"])
        if item["bcos_tier"] not in TIERS:
            raise ValueError(f"{item['id']} has invalid tier: {item['bcos_tier']}")
        if item["category"] not in CATEGORIES:
            raise ValueError(f"{item['id']} has invalid category: {item['category']}")
        if not SBOM_RE.match(item["sbom_hash"]):
            raise ValueError(f"{item['id']} has invalid sbom_hash")
    return projects


def badge(entry: dict) -> str:
    label = f"BCOS-{entry['bcos_tier']}"
    color = {"L0": "64748b", "L1": "2563eb", "L2": "16a34a"}[entry["bcos_tier"]]
    return f"https://img.shields.io/badge/{label}-{entry['id']}-{color}?style=flat-square"


def project_card(entry: dict) -> str:
    search = " ".join(
        str(entry[key])
        for key in ("name", "url", "github", "category", "bcos_tier", "review_note")
    ).lower()
    embed = f"![{entry['name']} BCOS badge]({badge(entry)})"
    return f"""
    <article class="project" data-tier="{esc(entry['bcos_tier'])}" data-category="{esc(entry['category'])}" data-search="{esc(search)}">
      <div class="project-head">
        <div>
          <h2>{esc(entry['name'])}</h2>
          <p class="category">{esc(entry['category'])}</p>
        </div>
        <span class="tier tier-{esc(entry['bcos_tier']).lower()}">{esc(entry['bcos_tier'])}</span>
      </div>
      <dl>
        <dt>Project URL</dt><dd><a href="{esc(entry['url'])}">{esc(entry['url'])}</a></dd>
        <dt>GitHub</dt><dd><a href="{esc(entry['github'])}">{esc(entry['github'])}</a></dd>
        <dt>Latest SHA</dt><dd><code>{esc(entry['latest_attested_sha'])}</code></dd>
        <dt>SBOM Hash</dt><dd><code>{esc(entry['sbom_hash'])}</code></dd>
        <dt>Review Note</dt><dd>{esc(entry['review_note'])}</dd>
      </dl>
      <div class="badge-row">
        <img src="{esc(badge(entry))}" alt="{esc(entry['name'])} BCOS badge">
        <button type="button" data-copy="{esc(embed)}">Copy badge</button>
      </div>
      <pre>{esc(embed)}</pre>
    </article>
    """


def build(projects: list[dict]) -> str:
    tier_options = "\n".join(f'<option value="{tier}">{tier}</option>' for tier in sorted(TIERS))
    category_options = "\n".join(
        f'<option value="{category}">{category}</option>' for category in sorted(CATEGORIES)
    )
    rows = "\n".join(project_card(project) for project in projects)
    stats = {
        "total": len(projects),
        "l2": sum(1 for project in projects if project["bcos_tier"] == "L2"),
        "l1": sum(1 for project in projects if project["bcos_tier"] == "L1"),
        "l0": sum(1 for project in projects if project["bcos_tier"] == "L0"),
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BCOS Certified Directory</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f8fb;
      color: #172033;
    }}
    body {{ margin: 0; }}
    header {{
      background: #122033;
      color: #f8fafc;
      padding: 28px clamp(18px, 4vw, 48px);
      border-bottom: 4px solid #38bdf8;
    }}
    h1 {{ margin: 0; font-size: clamp(28px, 4vw, 46px); letter-spacing: 0; }}
    header p {{ margin: 8px 0 0; color: #cbd5e1; max-width: 860px; }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 22px clamp(16px, 3vw, 34px) 56px; }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(220px, 1fr) 180px 220px;
      gap: 12px;
      align-items: end;
      margin: 18px 0;
    }}
    label {{ display: grid; gap: 6px; font-size: 13px; font-weight: 700; color: #475569; }}
    input, select {{
      height: 40px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 0 12px;
      font: inherit;
      background: white;
      color: #0f172a;
    }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 18px 0 20px; }}
    .stat {{ background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 14px; }}
    .stat b {{ display: block; font-size: 26px; }}
    .stat span {{ color: #64748b; font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 14px; }}
    .project {{ background: white; border: 1px solid #d8e0ea; border-radius: 8px; padding: 16px; }}
    .project[hidden] {{ display: none; }}
    .project-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    h2 {{ margin: 0; font-size: 22px; letter-spacing: 0; }}
    .category {{ margin: 4px 0 0; color: #64748b; font-size: 13px; }}
    .tier {{ border-radius: 999px; padding: 5px 10px; font-weight: 800; font-size: 13px; }}
    .tier-l0 {{ background: #e2e8f0; color: #334155; }}
    .tier-l1 {{ background: #dbeafe; color: #1d4ed8; }}
    .tier-l2 {{ background: #dcfce7; color: #15803d; }}
    dl {{ display: grid; grid-template-columns: 118px minmax(0, 1fr); gap: 8px 12px; margin: 16px 0; }}
    dt {{ color: #64748b; font-weight: 700; font-size: 13px; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    code, pre {{ background: #f1f5f9; border: 1px solid #d8e0ea; border-radius: 6px; }}
    code {{ padding: 2px 5px; }}
    pre {{ padding: 10px; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; color: #334155; }}
    a {{ color: #0f69a7; }}
    .badge-row {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
    button {{ height: 34px; border: 1px solid #94a3b8; background: #f8fafc; border-radius: 6px; cursor: pointer; }}
    @media (max-width: 780px) {{
      .toolbar, .stats {{ grid-template-columns: 1fr; }}
      dl {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>BCOS Certified Directory</h1>
    <p>Browse certified projects with trust metadata upfront: tier, attested commit, SBOM hash, and a short human/agent review note.</p>
  </header>
  <main>
    <section class="stats" aria-label="Directory stats">
      <div class="stat"><b>{stats['total']}</b><span>Total projects</span></div>
      <div class="stat"><b>{stats['l2']}</b><span>L2 certified</span></div>
      <div class="stat"><b>{stats['l1']}</b><span>L1 verified</span></div>
      <div class="stat"><b>{stats['l0']}</b><span>L0 tracked</span></div>
    </section>
    <section class="toolbar" aria-label="Search and filters">
      <label>Search<input id="search" type="search" placeholder="Project, repo, note, category"></label>
      <label>Tier<select id="tier"><option value="">All tiers</option>{tier_options}</select></label>
      <label>Category<select id="category"><option value="">All categories</option>{category_options}</select></label>
    </section>
    <section id="projects" class="grid">{rows}</section>
  </main>
  <script>
    const search = document.querySelector("#search");
    const tier = document.querySelector("#tier");
    const category = document.querySelector("#category");
    const cards = [...document.querySelectorAll(".project")];
    function applyFilters() {{
      const q = search.value.trim().toLowerCase();
      const wantedTier = tier.value;
      const wantedCategory = category.value;
      for (const card of cards) {{
        const matchSearch = !q || card.dataset.search.includes(q);
        const matchTier = !wantedTier || card.dataset.tier === wantedTier;
        const matchCategory = !wantedCategory || card.dataset.category === wantedCategory;
        card.hidden = !(matchSearch && matchTier && matchCategory);
      }}
    }}
    search.addEventListener("input", applyFilters);
    tier.addEventListener("change", applyFilters);
    category.addEventListener("change", applyFilters);
    document.addEventListener("click", async event => {{
      const button = event.target.closest("button[data-copy]");
      if (!button) return;
      await navigator.clipboard.writeText(button.dataset.copy);
      const old = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => button.textContent = old, 1000);
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    projects = load_projects()
    DIST.mkdir(exist_ok=True)
    OUT.write_text(build(projects), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} for {len(projects)} projects")


if __name__ == "__main__":
    main()
