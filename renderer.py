"""Self-contained HTML renderer for PolyGraph."""

from __future__ import annotations

import html
import json
from typing import Any


def render_html(graph: dict[str, Any], title: str = "PolyGraph") -> str:
    """Return a standalone HTML document for the graph."""

    data = json.dumps(graph, ensure_ascii=False)
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #071013;
      --panel: rgba(12, 19, 24, 0.88);
      --panel-strong: rgba(18, 29, 36, 0.96);
      --line: rgba(148, 163, 184, 0.28);
      --text: #eef6f8;
      --muted: #9fb3bd;
      --accent: #2dd4bf;
      --hot: #f97316;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: radial-gradient(circle at 28% 18%, #10232a 0, #071013 42%, #030607 100%);
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    canvas {{
      display: block;
      width: 100vw;
      height: 100vh;
      cursor: grab;
    }}
    canvas.dragging {{ cursor: grabbing; }}
    button, input {{
      font: inherit;
      letter-spacing: 0;
    }}
    .topbar {{
      position: fixed;
      left: 18px;
      right: 18px;
      top: 14px;
      z-index: 5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      pointer-events: none;
    }}
    .brand {{
      min-width: 0;
      pointer-events: auto;
    }}
    .brand h1 {{
      margin: 0;
      font-size: clamp(20px, 2vw, 30px);
      font-weight: 800;
      line-height: 1.05;
    }}
    .brand p {{
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .toolbar {{
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px;
      border: 1px solid var(--line);
      background: var(--panel);
      backdrop-filter: blur(16px);
      border-radius: 8px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
    }}
    .icon-button {{
      width: 36px;
      height: 36px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 8px;
      color: var(--text);
      background: rgba(255, 255, 255, 0.06);
      display: grid;
      place-items: center;
      cursor: pointer;
    }}
    .icon-button:hover {{ border-color: rgba(45, 212, 191, 0.65); color: #a7fff2; }}
    .search {{
      width: min(34vw, 340px);
      min-width: 190px;
      height: 36px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 8px;
      padding: 0 12px;
      color: var(--text);
      outline: none;
      background: rgba(255, 255, 255, 0.07);
    }}
    .search:focus {{ border-color: rgba(45, 212, 191, 0.78); }}
    .panel {{
      position: fixed;
      z-index: 4;
      right: 18px;
      top: 76px;
      width: min(330px, calc(100vw - 36px));
      max-height: calc(100vh - 104px);
      overflow: auto;
      border: 1px solid var(--line);
      background: var(--panel);
      backdrop-filter: blur(16px);
      border-radius: 8px;
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
    }}
    .panel section {{
      padding: 14px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.16);
    }}
    .panel section:last-child {{ border-bottom: 0; }}
    .panel h2 {{
      margin: 0 0 10px;
      font-size: 12px;
      color: #c6d6dc;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }}
    .stat {{
      min-width: 0;
      padding: 10px;
      border: 1px solid rgba(148, 163, 184, 0.16);
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
    }}
    .stat b {{
      display: block;
      font-size: 18px;
      line-height: 1;
    }}
    .stat span {{
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
    }}
    .toggle, .category {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 8px 0;
      color: #d8e7eb;
    }}
    .toggle input, .category input {{
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }}
    .segmented {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 4px;
      padding: 4px;
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
    }}
    .segmented label {{
      position: relative;
      min-width: 0;
    }}
    .segmented input {{
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }}
    .segmented span {{
      display: block;
      min-width: 0;
      padding: 8px 10px;
      border-radius: 6px;
      color: var(--muted);
      text-align: center;
      cursor: pointer;
    }}
    .segmented input:checked + span {{
      color: #04201d;
      background: var(--accent);
      font-weight: 800;
    }}
    .swatch {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      flex: 0 0 12px;
      box-shadow: 0 0 16px currentColor;
    }}
    .category-name {{
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }}
    .legend {{
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    .legend-row {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .line-sample {{
      width: 28px;
      height: 3px;
      border-radius: 99px;
    }}
    .details {{
      position: fixed;
      left: 18px;
      bottom: 18px;
      z-index: 6;
      width: min(430px, calc(100vw - 36px));
      max-height: min(54vh, 430px);
      overflow: auto;
      border: 1px solid var(--line);
      background: var(--panel-strong);
      backdrop-filter: blur(16px);
      border-radius: 8px;
      padding: 14px;
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
      display: none;
    }}
    .details.visible {{ display: block; }}
    .details h2 {{
      margin: 0;
      font-size: 16px;
      overflow-wrap: anywhere;
    }}
    .details .meta {{
      margin: 6px 0 12px;
      color: var(--muted);
      font-size: 12px;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }}
    .chip {{
      max-width: 100%;
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 999px;
      color: #d9e7eb;
      background: rgba(255, 255, 255, 0.06);
      padding: 4px 8px;
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .empty {{
      color: var(--muted);
      font-size: 12px;
    }}
    .tooltip {{
      position: fixed;
      z-index: 7;
      pointer-events: none;
      max-width: 300px;
      padding: 10px 12px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 8px;
      background: rgba(5, 10, 13, 0.92);
      box-shadow: 0 18px 45px rgba(0, 0, 0, 0.34);
      display: none;
    }}
    .tooltip b {{ display: block; overflow-wrap: anywhere; }}
    .tooltip span {{ color: var(--muted); font-size: 12px; }}
    @media (max-width: 780px) {{
      .topbar {{
        left: 10px;
        right: 10px;
        top: 10px;
        align-items: stretch;
        flex-direction: column;
      }}
      .toolbar {{
        width: 100%;
      }}
      .search {{
        flex: 1 1 auto;
        min-width: 0;
        width: auto;
      }}
      .panel {{
        right: 10px;
        top: auto;
        bottom: 10px;
        max-height: 42vh;
      }}
      .details {{
        left: 10px;
        bottom: calc(42vh + 22px);
        max-height: 30vh;
      }}
    }}
  </style>
</head>
<body>
  <canvas id="graph"></canvas>
  <div class="topbar">
    <div class="brand">
      <h1>PolyGraph</h1>
      <p id="subtitle"></p>
    </div>
    <div class="toolbar">
      <input id="search" class="search" type="search" placeholder="Search files or functions">
      <button id="reset" class="icon-button" title="Reset camera" aria-label="Reset camera">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M3 12a9 9 0 1 0 3-6.7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M3 4v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
  <aside class="panel">
    <section>
      <h2>Overview</h2>
      <div class="stats">
        <div class="stat"><b id="nodeCount">0</b><span>files</span></div>
        <div class="stat"><b id="edgeCount">0</b><span>links</span></div>
        <div class="stat"><b id="folderCount">0</b><span>folders</span></div>
      </div>
    </section>
    <section>
      <h2>Layers</h2>
      <div class="segmented" aria-label="View mode">
        <label><input name="viewMode" value="3d" type="radio" checked><span>3D</span></label>
        <label><input name="viewMode" value="linear" type="radio"><span>Linear</span></label>
      </div>
      <label class="toggle"><span>External imports</span><input id="showExternal" type="checkbox"></label>
      <label class="toggle"><span>Function calls</span><input id="showFunctions" type="checkbox" checked></label>
    </section>
    <section>
      <h2>Categories</h2>
      <div id="categories"></div>
    </section>
    <section>
      <h2>Edges</h2>
      <div class="legend">
        <div class="legend-row"><span class="line-sample" style="background:#4aa3ff"></span>Imports</div>
        <div class="legend-row"><span class="line-sample" style="background:#f97316"></span>Function calls</div>
        <div class="legend-row"><span class="line-sample" style="background:#94a3b8"></span>External imports</div>
      </div>
    </section>
  </aside>
  <div id="details" class="details"></div>
  <div id="tooltip" class="tooltip"></div>
  <script id="polygraph-data" type="application/json">{data}</script>
  <script>
(() => {{
  "use strict";

  const raw = JSON.parse(document.getElementById("polygraph-data").textContent);
  const categoryColors = raw.meta.categories || {{}};
  const canvas = document.getElementById("graph");
  const ctx = canvas.getContext("2d");
  const tooltip = document.getElementById("tooltip");
  const details = document.getElementById("details");
  const searchInput = document.getElementById("search");
  const showExternalInput = document.getElementById("showExternal");
  const showFunctionsInput = document.getElementById("showFunctions");
  const viewModeInputs = [...document.querySelectorAll('input[name="viewMode"]')];

  let width = 0;
  let height = 0;
  let dpr = Math.min(window.devicePixelRatio || 1, 2);
  let rotationX = -0.58;
  let rotationY = 0.72;
  let linearRotation = 0;
  let zoom = 0.86;
  let panX = 0;
  let panY = 0;
  let pointer = {{ x: -9999, y: -9999 }};
  let hovered = null;
  let selected = null;
  let searchTerm = "";
  let layoutMode = "3d";
  let frame = 0;
  let dragging = false;
  let panning = false;
  let lastPointer = null;
  let connectedIds = new Set();
  let sceneNodeById = new Map();
  let linearPlan = null;

  const localNodes = raw.nodes.map((node, index) => ({{
    ...node,
    index,
    external: false,
    x: 0,
    y: 0,
    z: 0,
    vx: 0,
    vy: 0,
    vz: 0,
    radius: nodeRadius(node),
    screenX: 0,
    screenY: 0,
    screenR: 0,
    depth: 0
  }}));
  const nodeById = new Map(localNodes.map(node => [node.id, node]));
  const folders = [...new Set(localNodes.map(node => node.folder))].sort();
  const folderZ = new Map(folders.map((folder, index) => [folder, (index - (folders.length - 1) / 2) * 220]));
  const categories = [...new Set(localNodes.map(node => node.category))].sort();
  const enabledCategories = new Set(categories);

  let nodes = [];
  let edges = [];

  function seedLayout() {{
    const byFolderCount = new Map();
    localNodes.forEach((node, index) => {{
      const count = byFolderCount.get(node.folder) || 0;
      byFolderCount.set(node.folder, count + 1);
      const angle = (count * 2.399963 + index * 0.31) % (Math.PI * 2);
      const radius = 90 + Math.sqrt(count + 1) * 34;
      node.x = Math.cos(angle) * radius + (Math.random() - 0.5) * 24;
      node.y = Math.sin(angle) * radius + (Math.random() - 0.5) * 24;
      node.z = folderZ.get(node.folder) || 0;
      node.vx = 0;
      node.vy = 0;
      node.vz = 0;
    }});
  }}

  function nodeRadius(node) {{
    return Math.max(7, Math.min(28, 6 + Math.sqrt(Math.max(1, node.lines)) * 0.8));
  }}

  function rebuildScene() {{
    const includeExternal = showExternalInput.checked;
    const showFunctions = showFunctionsInput.checked;
    const nextNodes = [...localNodes];
    const nextEdges = raw.edges
      .filter(edge => showFunctions || edge.type !== "function_call")
      .map((edge, index) => ({{
        ...edge,
        index,
        sourceNode: nodeById.get(edge.source),
        targetNode: nodeById.get(edge.target),
        external: false
      }}))
      .filter(edge => edge.sourceNode && edge.targetNode);

    if (includeExternal) {{
      const externalMap = new Map();
      localNodes.forEach(source => {{
        (source.imports_external || []).forEach(name => {{
          const id = `external:${{name}}`;
          if (!externalMap.has(id)) {{
            const angle = externalMap.size * 1.618;
            const externalIndex = localNodes.length + externalMap.size;
            const ghost = {{
              id,
              path: name,
              folder: "external",
              category: name.startsWith("stdlib:") ? "utils" : "data",
              index: externalIndex,
              lines: 10,
              functions: [],
              classes: [],
              imports_local: [],
              imports_external: [],
              external: true,
              x: Math.cos(angle) * 420,
              y: Math.sin(angle) * 420,
              z: ((externalMap.size % 5) - 2) * 160,
              vx: 0,
              vy: 0,
              vz: 0,
              radius: 6,
              screenX: 0,
              screenY: 0,
              screenR: 0,
              depth: 0
            }};
            externalMap.set(id, ghost);
          }}
          const target = externalMap.get(id);
          nextEdges.push({{
            source: source.id,
            target: id,
            type: "external_import",
            index: nextEdges.length,
            sourceNode: source,
            targetNode: target,
            external: true
          }});
        }});
      }});
      nextNodes.push(...externalMap.values());
    }}

    nodes = nextNodes;
    edges = nextEdges;
    sceneNodeById = new Map(nodes.map(node => [node.id, node]));
    linearPlan = null;
    frame = 0;
    updateConnectedSet();
    updateCounts();
  }}

  function installCategoryControls() {{
    const wrap = document.getElementById("categories");
    wrap.innerHTML = categories.map(category => `
      <label class="category">
        <span class="category-name">
          <span class="swatch" style="background:${{categoryColors[category] || "#94a3b8"}};color:${{categoryColors[category] || "#94a3b8"}}"></span>
          <span>${{escapeHtml(category)}}</span>
        </span>
        <input data-category="${{escapeHtml(category)}}" type="checkbox" checked>
      </label>
    `).join("");
    wrap.querySelectorAll("input").forEach(input => {{
      input.addEventListener("change", () => {{
        if (input.checked) enabledCategories.add(input.dataset.category);
        else enabledCategories.delete(input.dataset.category);
        linearPlan = null;
        frame = 0;
      }});
    }});
  }}

  function updateCounts() {{
    document.getElementById("subtitle").textContent = `${{raw.meta.node_count}} files, ${{raw.meta.edge_count}} links, ${{raw.meta.depth}} depth`;
    document.getElementById("nodeCount").textContent = raw.meta.node_count;
    document.getElementById("edgeCount").textContent = raw.meta.edge_count;
    document.getElementById("folderCount").textContent = folders.length;
  }}

  function resize() {{
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${{width}}px`;
    canvas.style.height = `${{height}}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }}

  function tick() {{
    const visibleNodes = nodes.filter(isNodeVisible);
    const visibleSet = new Set(visibleNodes.map(node => node.id));
    const visibleEdges = edges.filter(edge => visibleSet.has(edge.source) && visibleSet.has(edge.target));

    if (layoutMode === "linear") {{
      tickLinear(visibleNodes, visibleEdges);
      return;
    }}

    for (let i = 0; i < visibleNodes.length; i += 1) {{
      const a = visibleNodes[i];
      for (let j = i + 1; j < visibleNodes.length; j += 1) {{
        const b = visibleNodes[j];
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        let dz = a.z - b.z;
        let dist2 = dx * dx + dy * dy + dz * dz + 80;
        const force = (a.external || b.external ? 900 : 1600) / dist2;
        const inv = 1 / Math.sqrt(dist2);
        dx *= inv; dy *= inv; dz *= inv;
        a.vx += dx * force; a.vy += dy * force; a.vz += dz * force;
        b.vx -= dx * force; b.vy -= dy * force; b.vz -= dz * force;
      }}
    }}

    visibleEdges.forEach(edge => {{
      const a = edge.sourceNode;
      const b = edge.targetNode;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dz = b.z - a.z;
      const dist = Math.max(1, Math.sqrt(dx * dx + dy * dy + dz * dz));
      const desired = edge.external ? 320 : edge.type === "function_call" ? 112 : 145;
      const force = (dist - desired) * (edge.type === "function_call" ? 0.0028 : 0.0022);
      const fx = dx / dist * force;
      const fy = dy / dist * force;
      const fz = dz / dist * force;
      a.vx += fx; a.vy += fy; a.vz += fz;
      b.vx -= fx; b.vy -= fy; b.vz -= fz;
    }});

    visibleNodes.forEach(node => {{
      const targetZ = node.external ? node.z : (folderZ.get(node.folder) || 0);
      node.vz += (targetZ - node.z) * 0.002;
      node.vx += (0 - node.x) * 0.0008;
      node.vy += (0 - node.y) * 0.0008;
      node.vx *= 0.84;
      node.vy *= 0.84;
      node.vz *= 0.84;
      node.x += node.vx;
      node.y += node.vy;
      node.z += node.vz;
    }});
  }}

  function tickLinear(visibleNodes, visibleEdges) {{
    const plan = getLinearPlan(visibleNodes, visibleEdges);

    plan.positions.forEach(position => {{
      const node = sceneNodeById.get(position.id);
      if (!node) return;
      node.vx += (position.x - node.x) * 0.08;
      node.vy += (position.y - node.y) * 0.08;
      node.vz += (0 - node.z) * 0.08;
    }});

    visibleEdges.forEach(edge => {{
      const a = edge.sourceNode;
      const b = edge.targetNode;
      if (layoutMode === "linear" && edge.external) return;
      const sameLayer = (plan.layers.get(a.id) || 0) === (plan.layers.get(b.id) || 0);
      if (!sameLayer) return;
      const dy = a.y - b.y;
      if (Math.abs(dy) < 48) {{
        const push = dy >= 0 ? 0.55 : -0.55;
        a.vy += push;
        b.vy -= push;
      }}
    }});

    visibleNodes.forEach(node => {{
      node.vx *= 0.62;
      node.vy *= 0.62;
      node.vz *= 0.62;
      node.x += node.vx;
      node.y += node.vy;
      node.z += node.vz;
    }});
  }}

  function getLinearPlan(visibleNodes, visibleEdges) {{
    if (linearPlan) return linearPlan;

    const layers = linearLayers(visibleNodes, visibleEdges);
    const grouped = new Map();
    visibleNodes.forEach(node => {{
      const layer = layers.get(node.id) || 0;
      if (!grouped.has(layer)) grouped.set(layer, []);
      grouped.get(layer).push(node);
    }});

    const orderedLayers = [...grouped.keys()].sort((a, b) => a - b);
    const columnGap = 230;
    const rowGap = showExternalInput.checked ? 46 : 58;
    const centerLayer = (orderedLayers.length - 1) / 2;
    const positions = [];

    orderedLayers.forEach((layer, layerIndex) => {{
      const column = grouped.get(layer).sort((a, b) => {{
        const categoryCompare = a.category.localeCompare(b.category);
        return categoryCompare || a.path.localeCompare(b.path);
      }});
      const yOffset = (column.length - 1) * rowGap / 2;
      column.forEach((node, row) => {{
        const jitter = (((node.index || 0) % 5) - 2) * 5;
        positions.push({{
          id: node.id,
          x: (layerIndex - centerLayer) * columnGap,
          y: row * rowGap - yOffset + jitter
        }});
      }});
    }});

    linearPlan = {{ layers, positions }};
    return linearPlan;
  }}

  function linearLayers(visibleNodes, visibleEdges) {{
    const ids = new Set(visibleNodes.map(node => node.id));
    const outgoing = new Map(visibleNodes.map(node => [node.id, []]));
    const incomingCount = new Map(visibleNodes.map(node => [node.id, 0]));
    visibleEdges.forEach(edge => {{
      if (!ids.has(edge.source) || !ids.has(edge.target)) return;
      outgoing.get(edge.source).push(edge.target);
      incomingCount.set(edge.target, (incomingCount.get(edge.target) || 0) + 1);
    }});

    const starts = visibleNodes
      .filter(node => node.category === "entry" || (incomingCount.get(node.id) || 0) === 0)
      .sort((a, b) => a.path.localeCompare(b.path));
    const queue = starts.length ? [...starts] : [...visibleNodes].sort((a, b) => a.path.localeCompare(b.path));
    const layers = new Map(queue.map(node => [node.id, node.category === "entry" ? 0 : 1]));

    while (queue.length) {{
      const node = queue.shift();
      const nextLayer = (layers.get(node.id) || 0) + 1;
      for (const target of outgoing.get(node.id) || []) {{
        if (!layers.has(target) || nextLayer < layers.get(target)) {{
          layers.set(target, Math.min(nextLayer, 7));
          const targetNode = sceneNodeById.get(target);
          if (targetNode && !queue.includes(targetNode)) queue.push(targetNode);
        }}
      }}
    }}

    visibleNodes.forEach(node => {{
      if (!layers.has(node.id)) {{
        const fallback = node.external ? 7 : Math.min(folders.indexOf(node.folder) + 1, 6);
        layers.set(node.id, fallback < 0 ? 1 : fallback);
      }}
    }});
    return layers;
  }}

  function render() {{
    frame += 1;
    if (layoutMode === "linear") {{
      tick();
    }} else if (frame < 900) {{
      for (let i = 0; i < 2; i += 1) tick();
    }} else {{
      tick();
    }}

    ctx.clearRect(0, 0, width, height);
    drawBackdrop();
    nodes.forEach(projectNode);
    const visibleNodes = nodes.filter(isNodeVisible);
    const visibleSet = new Set(visibleNodes.map(node => node.id));
    const visibleEdges = edges.filter(edge => visibleSet.has(edge.source) && visibleSet.has(edge.target));

    visibleEdges
      .slice()
      .sort((a, b) => (a.sourceNode.depth + a.targetNode.depth) - (b.sourceNode.depth + b.targetNode.depth))
      .forEach(edge => drawEdge(edge));

    hovered = findHovered(visibleNodes);
    visibleNodes
      .slice()
      .sort((a, b) => a.depth - b.depth)
      .forEach(node => drawNode(node));

    updateTooltip();
    requestAnimationFrame(render);
  }}

  function drawBackdrop() {{
    ctx.save();
    ctx.globalAlpha = 0.55;
    ctx.strokeStyle = "rgba(148, 163, 184, 0.08)";
    ctx.lineWidth = 1;
    const grid = 74 * zoom;
    const offsetX = (panX % grid + grid) % grid;
    const offsetY = (panY % grid + grid) % grid;
    for (let x = offsetX; x < width; x += grid) {{
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
    }}
    for (let y = offsetY; y < height; y += grid) {{
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
    }}
    ctx.restore();
  }}

  function projectNode(node) {{
    if (layoutMode === "linear") {{
      const cos = Math.cos(linearRotation);
      const sin = Math.sin(linearRotation);
      const x = node.x * cos - node.y * sin;
      const y = node.x * sin + node.y * cos;
      const scale = zoom;
      node.screenX = width / 2 + panX + x * scale;
      node.screenY = height / 2 + panY + y * scale;
      node.screenR = Math.max(3, node.radius * Math.min(1.18, scale));
      node.depth = y * 0.01;
      return;
    }}
    const cx = Math.cos(rotationX);
    const sx = Math.sin(rotationX);
    const cy = Math.cos(rotationY);
    const sy = Math.sin(rotationY);
    let x = node.x * cy - node.z * sy;
    let z = node.x * sy + node.z * cy;
    let y = node.y * cx - z * sx;
    z = node.y * sx + z * cx;
    const perspective = 680 / (680 + z);
    const scale = perspective * zoom;
    node.screenX = width / 2 + panX + x * scale;
    node.screenY = height / 2 + panY + y * scale;
    node.screenR = Math.max(3, node.radius * scale);
    node.depth = z;
  }}

  function drawEdge(edge) {{
    const a = edge.sourceNode;
    const b = edge.targetNode;
    const state = visibilityState(a, b);
    const color = edge.type === "function_call" ? "#f97316" : edge.external ? "#94a3b8" : "#4aa3ff";
    const alpha = state === "dim" ? 0.08 : edge.external ? (layoutMode === "linear" ? 0.1 : 0.18) : 0.42;
    const midX = (a.screenX + b.screenX) / 2 + Math.sin(edge.index * 1.9) * 18;
    const midY = (a.screenY + b.screenY) / 2 + Math.cos(edge.index * 1.7) * 18;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = edge.type === "function_call" ? 1.7 : 1.25;
    ctx.beginPath();
    ctx.moveTo(a.screenX, a.screenY);
    ctx.quadraticCurveTo(midX, midY, b.screenX, b.screenY);
    ctx.stroke();
    if (state !== "dim" && !(layoutMode === "linear" && edge.external)) {{
      drawParticle(a, b, midX, midY, color, edge.index);
    }}
    ctx.restore();
  }}

  function drawParticle(a, b, midX, midY, color, index) {{
    const t = ((performance.now() * 0.00018) + index * 0.071) % 1;
    const qx = quadratic(a.screenX, midX, b.screenX, t);
    const qy = quadratic(a.screenY, midY, b.screenY, t);
    ctx.globalAlpha = 0.85;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(qx, qy, 2.4, 0, Math.PI * 2);
    ctx.fill();
  }}

  function drawNode(node) {{
    const state = visibilityState(node);
    const color = node.external ? "#94a3b8" : (categoryColors[node.category] || "#34d399");
    const searched = searchTerm && matchesSearch(node);
    const active = node === hovered || node === selected || searched || connectedIds.has(node.id);
    const alpha = state === "dim" ? 0.18 : node.external ? 0.52 : 1;
    const radius = node.screenR * (active ? 1.22 : 1);
    ctx.save();
    ctx.globalAlpha = alpha;
    const gradient = ctx.createRadialGradient(
      node.screenX - radius * 0.34,
      node.screenY - radius * 0.42,
      radius * 0.1,
      node.screenX,
      node.screenY,
      radius
    );
    gradient.addColorStop(0, "#ffffff");
    gradient.addColorStop(0.18, color);
    gradient.addColorStop(1, "rgba(2, 6, 8, 0.86)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(node.screenX, node.screenY, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.lineWidth = active ? 2.4 : 1;
    ctx.strokeStyle = searched ? "#ffffff" : active ? color : "rgba(255,255,255,0.22)";
    ctx.stroke();
    if (active) {{
      ctx.globalAlpha = state === "dim" ? 0.14 : 0.22;
      ctx.strokeStyle = color;
      ctx.lineWidth = 8;
      ctx.beginPath();
      ctx.arc(node.screenX, node.screenY, radius + 5, 0, Math.PI * 2);
      ctx.stroke();
    }}
    if (radius > 8 && state !== "dim") {{
      ctx.globalAlpha = node.external ? 0.7 : 0.95;
      ctx.fillStyle = "#eef6f8";
      ctx.font = "12px Inter, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      const label = node.external ? node.path.replace(/^stdlib:/, "") : basename(node.path);
      ctx.fillText(label, node.screenX, node.screenY + radius + 6, 150);
    }}
    ctx.restore();
  }}

  function findHovered(visibleNodes) {{
    let best = null;
    let bestDist = 18;
    for (const node of visibleNodes) {{
      const dx = pointer.x - node.screenX;
      const dy = pointer.y - node.screenY;
      const dist = Math.sqrt(dx * dx + dy * dy) - node.screenR;
      if (dist < bestDist) {{
        bestDist = dist;
        best = node;
      }}
    }}
    return best;
  }}

  function updateTooltip() {{
    if (!hovered) {{
      tooltip.style.display = "none";
      return;
    }}
    tooltip.style.display = "block";
    tooltip.style.left = `${{Math.min(width - 320, pointer.x + 16)}}px`;
    tooltip.style.top = `${{Math.min(height - 120, pointer.y + 16)}}px`;
    tooltip.innerHTML = `
      <b>${{escapeHtml(hovered.path)}}</b>
      <span>${{escapeHtml(hovered.category)}} - ${{hovered.lines}} lines - ${{hovered.functions.length}} funcs - ${{hovered.classes.length}} classes</span>
    `;
  }}

  function showDetails(node) {{
    if (!node) {{
      details.classList.remove("visible");
      details.innerHTML = "";
      return;
    }}
    const functionChips = chips(node.functions);
    const classChips = chips(node.classes);
    const importChips = chips([...(node.imports_local || []), ...(node.imports_external || [])]);
    details.innerHTML = `
      <h2>${{escapeHtml(node.path)}}</h2>
      <div class="meta">${{escapeHtml(node.folder)}} - ${{escapeHtml(node.category)}} - ${{node.lines}} lines</div>
      <h2>Functions</h2>
      ${{functionChips}}
      <h2 style="margin-top:14px">Classes</h2>
      ${{classChips}}
      <h2 style="margin-top:14px">Imports</h2>
      ${{importChips}}
    `;
    details.classList.add("visible");
  }}

  function chips(items) {{
    if (!items || !items.length) return `<div class="empty">None found</div>`;
    return `<div class="chips">${{items.slice(0, 80).map(item => `<span class="chip">${{escapeHtml(item)}}</span>`).join("")}}</div>`;
  }}

  function updateConnectedSet() {{
    connectedIds = new Set();
    if (!selected) return;
    connectedIds.add(selected.id);
    edges.forEach(edge => {{
      if (edge.source === selected.id) connectedIds.add(edge.target);
      if (edge.target === selected.id) connectedIds.add(edge.source);
    }});
  }}

  function isNodeVisible(node) {{
    if (node.external) return showExternalInput.checked;
    return enabledCategories.has(node.category);
  }}

  function visibilityState(a, b = null) {{
    if (!selected && !searchTerm) return "normal";
    const ids = b ? [a.id, b.id] : [a.id];
    const selectedMatch = selected && ids.some(id => connectedIds.has(id));
    const searchMatch = ids.some(id => {{
      const node = sceneNodeById.get(id);
      return node && matchesSearch(node);
    }});
    return selectedMatch || searchMatch ? "normal" : "dim";
  }}

  function matchesSearch(node) {{
    if (!searchTerm) return false;
    const haystack = [
      node.path,
      node.folder,
      node.category,
      ...(node.functions || []),
      ...(node.classes || []),
      ...(node.imports_local || []),
      ...(node.imports_external || [])
    ].join(" ").toLowerCase();
    return haystack.includes(searchTerm);
  }}

  function quadratic(a, b, c, t) {{
    return (1 - t) * (1 - t) * a + 2 * (1 - t) * t * b + t * t * c;
  }}

  function basename(path) {{
    return path.split("/").pop();
  }}

  function escapeHtml(value) {{
    return String(value).replace(/[&<>"']/g, char => ({{
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\\"": "&quot;",
      "'": "&#39;"
    }}[char]));
  }}

  function eventPoint(event) {{
    return {{ x: event.clientX, y: event.clientY }};
  }}

  canvas.addEventListener("pointerdown", event => {{
    canvas.setPointerCapture(event.pointerId);
    lastPointer = eventPoint(event);
    dragging = event.button === 0;
    panning = event.button === 2;
    canvas.classList.add("dragging");
  }});

  canvas.addEventListener("pointermove", event => {{
    pointer = eventPoint(event);
    if (!lastPointer) return;
    const point = eventPoint(event);
    const dx = point.x - lastPointer.x;
    const dy = point.y - lastPointer.y;
    if (dragging) {{
      if (layoutMode === "linear") {{
        linearRotation += dx * 0.008;
      }} else {{
        rotationY += dx * 0.006;
        rotationX += dy * 0.006;
        rotationX = Math.max(-1.55, Math.min(1.55, rotationX));
      }}
    }}
    if (panning) {{
      panX += dx;
      panY += dy;
    }}
    lastPointer = point;
  }});

  canvas.addEventListener("pointerup", event => {{
    canvas.releasePointerCapture(event.pointerId);
    if (dragging && lastPointer && Math.abs(event.movementX) < 3 && Math.abs(event.movementY) < 3) {{
      selected = hovered === selected ? null : hovered;
      updateConnectedSet();
      showDetails(selected);
    }}
    dragging = false;
    panning = false;
    lastPointer = null;
    canvas.classList.remove("dragging");
  }});

  canvas.addEventListener("pointerleave", () => {{
    pointer = {{ x: -9999, y: -9999 }};
  }});

  canvas.addEventListener("contextmenu", event => event.preventDefault());
  canvas.addEventListener("wheel", event => {{
    event.preventDefault();
    const factor = Math.exp(-event.deltaY * 0.001);
    zoom = Math.max(0.18, Math.min(4, zoom * factor));
  }}, {{ passive: false }});

  searchInput.addEventListener("input", () => {{
    searchTerm = searchInput.value.trim().toLowerCase();
  }});

  viewModeInputs.forEach(input => {{
    input.addEventListener("change", () => {{
      if (!input.checked) return;
      layoutMode = input.value;
      zoom = layoutMode === "linear" ? 0.78 : 0.86;
      panX = 0;
      panY = 0;
      rotationX = -0.58;
      rotationY = 0.72;
      linearRotation = 0;
      frame = 0;
    }});
  }});
  showExternalInput.addEventListener("change", rebuildScene);
  showFunctionsInput.addEventListener("change", rebuildScene);
  document.getElementById("reset").addEventListener("click", () => {{
    rotationX = -0.58;
    rotationY = 0.72;
    linearRotation = 0;
    zoom = layoutMode === "linear" ? 0.78 : 0.86;
    panX = 0;
    panY = 0;
    selected = null;
    updateConnectedSet();
    showDetails(null);
  }});
  window.addEventListener("resize", resize);

  installCategoryControls();
  seedLayout();
  rebuildScene();
  resize();
  render();
}})();
  </script>
</body>
</html>
"""
