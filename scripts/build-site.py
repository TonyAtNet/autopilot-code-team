#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
构建 GitHub Pages 文档站点

扫描 product/ 和 engineering/ 目录下的 .md 文件，提取 Frontmatter 和摘要，
生成 docs/index.html 静态站点。

使用方法：
    python scripts/build-site.py

输出：
    docs/index.html
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENT_DIRS = [REPO_ROOT / "product", REPO_ROOT / "engineering"]
OUTPUT = REPO_ROOT / "docs" / "index.html"

# 颜色映射（Tailwind CSS 类名）
COLOR_MAP = {
    "red": "bg-red-50 border-red-200 text-red-700",
    "blue": "bg-blue-50 border-blue-200 text-blue-700",
    "green": "bg-green-50 border-green-200 text-green-700",
    "yellow": "bg-yellow-50 border-yellow-200 text-yellow-700",
    "magenta": "bg-pink-50 border-pink-200 text-pink-700",
    "cyan": "bg-cyan-50 border-cyan-200 text-cyan-700",
    "indigo": "bg-indigo-50 border-indigo-200 text-indigo-700",
    "orange": "bg-orange-50 border-orange-200 text-orange-700",
    "teal": "bg-teal-50 border-teal-200 text-teal-700",
    "purple": "bg-purple-50 border-purple-200 text-purple-700",
    "slate": "bg-slate-50 border-slate-200 text-slate-700",
}

DEFAULT_COLOR = "bg-slate-50 border-slate-200 text-slate-700"


def extract_frontmatter(content: str) -> dict:
    """提取 YAML Frontmatter"""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    frontmatter = content[3:end].strip()
    result = {}
    for line in frontmatter.splitlines():
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def extract_summary(content: str) -> str:
    """提取文件的第一段描述（作为摘要）"""
    # 去掉 frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:]

    # 去掉标题行
    lines = content.strip().splitlines()
    # 找到第一个非空且非标题行
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("---"):
            # 返回前 150 字
            return line[:200] + "..." if len(line) > 200 else line
    return ""


def extract_tools(content: str) -> list[str]:
    """提取工具链关键词（从 '可操作的现代工具链覆盖' 部分）"""
    tools = []
    # 简单匹配：在工具链段落后的列表项
    match = re.search(r"可操作的现代工具链覆盖.*?\n(.*?\n)\n", content, re.DOTALL)
    if match:
        block = match.group(1)
        # 提取粗体或列表项中的工具名
        found = re.findall(r"[\*\-]\s*(.+)", block)
        for f in found:
            # 提取工具名（通常用逗号分隔）
            parts = re.split(r"[,:：]", f)
            for p in parts:
                p = p.strip().strip("`")
                if p and len(p) < 30 and not p.startswith("-"):
                    tools.append(p)
    # 如果上面没提取到，从 content 中尝试提取已知工具名
    known_tools = ["Cursor", "Claude Code", "v0", "Lovable", "Bolt", "Tempo", "Framer", "MCP", "LangChain", "Langfuse", "Helicone", "Vercel", "Supabase", "Perplexity", "PostHog", "Amplitude", "Kimi", "Trae", "Roo Code", "Notion", "Linear", "GitHub", "Terraform", "Kubernetes", "Figma", "Sketch", "Tailwind", "React", "Next.js", "TypeScript", "Python", "Docker", "Git"]
    if not tools:
        for tool in known_tools:
            if tool in content:
                tools.append(tool)
    return tools[:8]  # 最多展示 8 个


def build_site():
    agents = []
    for agent_dir in AGENT_DIRS:
        if not agent_dir.exists():
            continue
        category = agent_dir.name
        for filepath in sorted(agent_dir.glob("*.md")):
            content = filepath.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            summary = extract_summary(content)
            tools = extract_tools(content)

            color = fm.get("color", "slate").lower()
            color_class = COLOR_MAP.get(color, DEFAULT_COLOR)

            agents.append({
                "name": fm.get("name", filepath.stem),
                "description": fm.get("description", ""),
                "summary": summary,
                "category": category,
                "color": color_class,
                "filename": filepath.name,
                "path": f"{category}/{filepath.name}",
                "tools": tools,
                "cmd": f"/{fm.get('name', filepath.stem)}",
            })

    # 生成 HTML
    agents_json = json.dumps(agents, ensure_ascii=False, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vibe Coding Agent Team</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  .agent-card {{ transition: all 0.2s ease; }}
  .agent-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.08); }}
  .copy-btn {{ transition: all 0.2s; }}
  .copy-btn.copied {{ background-color: #10b981; color: white; border-color: #10b981; }}
  .fade-in {{ animation: fadeIn 0.4s ease; }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body class="bg-slate-50 min-h-screen">

<!-- Header -->
<header class="bg-white border-b border-slate-200 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white font-bold text-sm">V</div>
        <div>
          <h1 class="text-lg font-bold text-slate-900">Vibe Coding Agent Team</h1>
          <p class="text-xs text-slate-500">面向 AI IDE 的 21 个角色配置库</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="https://github.com" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          GitHub
        </a>
      </div>
    </div>
  </div>
</header>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

  <!-- Stats -->
  <div class="flex gap-4 mb-8">
    <div class="bg-white rounded-xl border border-slate-200 px-4 py-3 flex items-center gap-3">
      <div class="text-2xl font-bold text-slate-900">{len(agents)}</div>
      <div class="text-xs text-slate-500">角色</div>
    </div>
    <div class="bg-white rounded-xl border border-slate-200 px-4 py-3 flex items-center gap-3">
      <div class="text-2xl font-bold text-slate-900">2</div>
      <div class="text-xs text-slate-500">分类</div>
    </div>
  </div>

  <!-- Search & Filter -->
  <div class="bg-white rounded-xl border border-slate-200 p-4 mb-6">
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="flex-1 relative">
        <input type="text" id="search" placeholder="搜索角色、工具或描述..." 
          class="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent">
        <svg class="w-4 h-4 text-slate-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      </div>
      <div class="flex gap-2">
        <button onclick="filterCategory('all')" id="btn-all" class="filter-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-900 text-white">全部</button>
        <button onclick="filterCategory('product')" id="btn-product" class="filter-btn px-4 py-2 rounded-lg text-sm font-medium bg-white text-slate-600 border border-slate-200 hover:bg-slate-50">产品</button>
        <button onclick="filterCategory('engineering')" id="btn-engineering" class="filter-btn px-4 py-2 rounded-lg text-sm font-medium bg-white text-slate-600 border border-slate-200 hover:bg-slate-50">工程</button>
      </div>
    </div>
  </div>

  <!-- Agent Grid -->
  <div id="agent-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>

  <!-- No results -->
  <div id="no-results" class="hidden text-center py-16">
    <div class="text-slate-400 text-sm">没有找到匹配的角色</div>
  </div>

</main>

<!-- Footer -->
<footer class="border-t border-slate-200 bg-white mt-16">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <p class="text-xs text-slate-500">
        Vibe Coding Agent Team  MIT License
      </p>
      <p class="text-xs text-slate-400">
        用 AI 团队，做 Vibe 产品
      </p>
    </div>
  </div>
</footer>

<script>
const agents = {agents_json};
let currentCategory = 'all';
let currentSearch = '';

function render() {{
  const grid = document.getElementById('agent-grid');
  const noResults = document.getElementById('no-results');
  
  const filtered = agents.filter(a => {{
    const matchCat = currentCategory === 'all' || a.category === currentCategory;
    const s = currentSearch.toLowerCase();
    const matchSearch = !s || 
      a.name.toLowerCase().includes(s) || 
      a.description.toLowerCase().includes(s) ||
      a.summary.toLowerCase().includes(s) ||
      a.tools.some(t => t.toLowerCase().includes(s));
    return matchCat && matchSearch;
  }});

  if (filtered.length === 0) {{
    grid.innerHTML = '';
    noResults.classList.remove('hidden');
    return;
  }}
  noResults.classList.add('hidden');

  grid.innerHTML = filtered.map(a => {{
    const toolsTags = a.tools.slice(0, 5).map(t => 
      `<span class="text-[10px] px-2 py-0.5 rounded bg-white/80 border border-slate-200 text-slate-600">${{t}}</span>`
    ).join('');
    
    const cmdTag = a.name === 'vibe-project-manager'
      ? `<span class="text-[11px] font-mono bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded">/vibe-project-manager "我想做..."</span>`
      : `<span class="text-[11px] font-mono bg-slate-100 text-slate-500 px-2 py-0.5 rounded">${{a.cmd}} &lt;task&gt;</span>`;
    
    return `
      <div class="agent-card bg-white rounded-xl border border-slate-200 p-5 fade-in">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full ${{a.color.split(' ')[0].replace('bg-', '').replace('50', '500')}}"></span>
            <span class="text-xs font-medium text-slate-500 uppercase tracking-wide">${{a.category}}</span>
            ${{a.name === 'vibe-project-manager' ? '<span class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-600 font-medium">入口</span>' : ''}}
          </div>
          <button onclick="copyAgent('${{a.path}}')" class="copy-btn text-xs px-3 py-1 rounded border border-slate-200 text-slate-600 hover:bg-slate-50" id="btn-${{a.path}}">
            复制
          </button>
        </div>
        <h3 class="text-base font-bold text-slate-900 mb-1">${{a.name}}</h3>
        <p class="text-xs text-slate-500 mb-2 leading-relaxed">${{a.description}}</p>
        <div class="mb-3">${{cmdTag}}</div>
        <p class="text-xs text-slate-600 mb-4 leading-relaxed line-clamp-2">${{a.summary}}</p>
        <div class="flex flex-wrap gap-1.5">${{toolsTags}}</div>
      </div>
    `;
  }}).join('');
}}

async function copyAgent(path) {{
  try {{
    const res = await fetch(path);
    const text = await res.text();
    await navigator.clipboard.writeText(text);
    const btn = document.getElementById('btn-' + path);
    const original = btn.textContent;
    btn.textContent = '已复制';
    btn.classList.add('copied');
    setTimeout(() => {{
      btn.textContent = original;
      btn.classList.remove('copied');
    }}, 2000);
  }} catch (e) {{
    alert('复制失败，请手动访问：' + path);
  }}
}}

function filterCategory(cat) {{
  currentCategory = cat;
  document.querySelectorAll('.filter-btn').forEach(b => {{
    b.classList.remove('bg-slate-900', 'text-white');
    b.classList.add('bg-white', 'text-slate-600');
  }});
  const active = document.getElementById('btn-' + cat);
  active.classList.remove('bg-white', 'text-slate-600');
  active.classList.add('bg-slate-900', 'text-white');
  render();
}}

document.getElementById('search').addEventListener('input', (e) => {{
  currentSearch = e.target.value;
  render();
}});

render();
</script>

</body>
</html>
'''

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"站点已生成: {OUTPUT}")
    print(f"共 {len(agents)} 个角色")


if __name__ == "__main__":
    build_site()
