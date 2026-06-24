#!/usr/bin/env python3
"""Render a static codebase understanding site from understanding_graph.json."""

from __future__ import annotations

import argparse
import html
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


LABELS_EN: dict[str, Any] = {
    "filterModules": "Filter modules",
    "moduleMap": "Module Map",
    "selectedModule": "Selected Module",
    "coreFlows": "Core Flows",
    "evidence": "Evidence",
    "openQuestions": "Open Questions",
    "graphAria": "Module relationship graph",
    "legend": "Legend",
    "modules": "modules",
    "relations": "relations",
    "moduleKind": "module",
    "defaultGroup": "Code",
    "noSummary": "No summary provided.",
    "incoming": "Incoming",
    "outgoing": "Outgoing",
    "noneListed": "none listed",
    "noFlows": "No flows provided.",
    "flowFallback": "Flow",
    "stepFallback": "Step",
    "noEvidence": "No evidence notes provided.",
    "evidenceFallback": "Evidence",
    "noQuestions": "No open questions listed.",
    "pathLabel": "Path",
    "groupLabel": "Group",
    "meaningTitle": "Functional Meaning",
    "nextReadTitle": "Next Read",
    "signalsTitle": "Signals",
    "metricsTitle": "Metrics",
    "relationsTitle": "Relations",
    "noSignals": "No signals listed.",
    "noMetrics": "No metrics listed.",
    "edgeFallback": "relates",
    "quickstartTitle": "Quickstart",
    "caseStudyTitle": "Case Study",
    "chaptersTitle": "Chapters",
    "learningGoalsTitle": "Learning Goals",
    "whyThisPathTitle": "Why This Path",
    "projectTypesTitle": "Project Types",
    "evidenceTypeTitle": "Evidence",
    "takeawayTitle": "Takeaway",
    "viewModule": "View Module",
    "noGuide": "No guided learning path provided.",
    "readerModeTitle": "Reader Mode",
    "studyPathTitle": "Study Path",
    "mapFirstTitle": "Map-first view",
    "mapFirstCaption": "Nodes and relations are useful later, but they do not explain where to begin.",
    "lessonFirstTitle": "Lesson-first view",
    "lessonFirstCaption": "Start from a real task, follow chapters, then use the graph as a reference.",
    "referenceIndexTitle": "Reference Index",
    "referenceIndexIntro": "Use this after the lesson gives you a concrete question or module to inspect.",
    "moduleIndexTitle": "Module Index",
    "chaptersNavTitle": "Chapters",
    "casePathTitle": "Walkthrough",
    "guidingQuestionTitle": "Guiding Question",
    "principleTitle": "Principle",
    "kindLabels": {
        "skill": "skill",
        "entrypoint": "entrypoint",
        "module": "module",
        "script": "script",
        "external": "external",
        "data": "data",
        "test": "test",
        "config": "config",
        "document": "document",
    },
}

LABELS_ZH: dict[str, Any] = {
    "filterModules": "筛选模块",
    "moduleMap": "模块关系图",
    "selectedModule": "当前模块",
    "coreFlows": "核心流程",
    "evidence": "证据",
    "openQuestions": "开放问题",
    "graphAria": "模块关系图",
    "legend": "图例",
    "modules": "个模块",
    "relations": "条关系",
    "moduleKind": "模块",
    "defaultGroup": "代码",
    "noSummary": "暂无摘要。",
    "incoming": "流入",
    "outgoing": "流出",
    "noneListed": "未列出",
    "noFlows": "暂无流程。",
    "flowFallback": "流程",
    "stepFallback": "步骤",
    "noEvidence": "暂无证据说明。",
    "evidenceFallback": "证据",
    "noQuestions": "暂无开放问题。",
    "pathLabel": "路径",
    "groupLabel": "分组",
    "meaningTitle": "功能含义",
    "nextReadTitle": "下一步阅读",
    "signalsTitle": "证据信号",
    "metricsTitle": "指标",
    "relationsTitle": "连接关系",
    "noSignals": "暂无证据信号。",
    "noMetrics": "暂无指标。",
    "edgeFallback": "关联",
    "quickstartTitle": "快速入门",
    "caseStudyTitle": "案例讲解",
    "chaptersTitle": "章节路线",
    "learningGoalsTitle": "学习目标",
    "whyThisPathTitle": "为什么这样学",
    "projectTypesTitle": "项目类型",
    "evidenceTypeTitle": "证据类型",
    "takeawayTitle": "本步要点",
    "viewModule": "查看模块",
    "noGuide": "暂无引导式学习路径。",
    "readerModeTitle": "阅读模式",
    "studyPathTitle": "学习路径",
    "mapFirstTitle": "先看地图",
    "mapFirstCaption": "节点和关系适合后查，但它们不会告诉你应该从哪里开始。",
    "lessonFirstTitle": "先读教材",
    "lessonFirstCaption": "先从一个真实任务进入，按章节推进，再把图谱当作参考索引。",
    "referenceIndexTitle": "参考索引",
    "referenceIndexIntro": "当教材让你产生具体问题或想查某个模块时，再回到这里检索和看关系。",
    "moduleIndexTitle": "模块索引",
    "chaptersNavTitle": "章节",
    "casePathTitle": "讲解路径",
    "guidingQuestionTitle": "本章问题",
    "principleTitle": "原理",
    "kindLabels": {
        "skill": "技能",
        "entrypoint": "入口",
        "module": "模块",
        "script": "脚本",
        "external": "外部",
        "data": "数据",
        "test": "测试",
        "config": "配置",
        "document": "文档",
    },
}


HTML_TEMPLATE = """<!doctype html>
<html lang="__LANG__">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #202936;
      --muted: #617086;
      --line: #d8dee8;
      --soft-line: #e8edf4;
      --accent: #2563eb;
      --accent-soft: #e8f0ff;
      --skill: #0e7490;
      --entrypoint: #7c3aed;
      --module: #2563eb;
      --script: #d97706;
      --external: #059669;
      --data: #be123c;
      --test: #64748b;
      --shadow: 0 10px 28px rgba(25, 34, 48, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      padding: 28px clamp(18px, 4vw, 52px) 22px;
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }
    h1 {
      margin: 0;
      font-size: clamp(26px, 3vw, 42px);
      letter-spacing: 0;
      line-height: 1.1;
    }
    header p {
      margin: 10px 0 0;
      max-width: 980px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.55;
    }
	    main {
	      width: min(1180px, calc(100% - 24px));
	      margin: 0 auto;
	      padding: 24px 0 42px;
	    }
	    aside, section {
	      min-width: 0;
	    }
	    aside {
	      min-width: 0;
	    }
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      border: 0;
    }
    .search {
      width: 100%;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 10px;
      font-size: 14px;
      color: var(--ink);
      background: #fff;
    }
    .stats {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
    }
    .stat {
      border: 1px solid var(--soft-line);
      border-radius: 999px;
      padding: 3px 8px;
      background: #fbfcfe;
    }
    .node-list {
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }
    button.node {
      display: grid;
      grid-template-columns: 7px 1fr;
      gap: 8px;
      align-items: stretch;
      width: 100%;
      min-height: 56px;
      padding: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
      overflow: hidden;
    }
    button.node[aria-selected="true"] {
      border-color: var(--accent);
      background: var(--accent-soft);
    }
    .node-swatch {
      width: 7px;
      min-height: 100%;
      background: var(--module);
    }
    .node-copy {
      display: grid;
      gap: 3px;
      padding: 8px 9px 8px 0;
    }
    .kind {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .label {
      font-size: 14px;
      font-weight: 650;
      overflow-wrap: anywhere;
    }
    .node-path {
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }
	    .workspace {
	      display: grid;
	      gap: 24px;
	      min-width: 0;
	    }
	    section {
	      min-width: 0;
	    }
    .section-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    h2 {
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }
	    .guide-section[hidden] {
	      display: none;
	    }
	    .guide-shell {
	      display: grid;
	      gap: 22px;
	    }
	    .guide-hero {
	      display: grid;
	      grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
	      gap: 20px;
	      align-items: stretch;
	      background: var(--panel);
	      border: 1px solid var(--line);
	      border-radius: 8px;
	      padding: clamp(18px, 3vw, 28px);
	      box-shadow: var(--shadow);
	    }
	    .guide-hero-copy {
	      display: grid;
	      align-content: start;
	      gap: 12px;
	    }
	    .guide-kicker {
	      color: var(--accent);
	      font-size: 12px;
	      font-weight: 750;
	      text-transform: uppercase;
	    }
	    .guide-title {
	      margin: 0;
	      font-size: clamp(28px, 4vw, 52px);
	      line-height: 1.15;
	      letter-spacing: 0;
	    }
	    .problem-compare {
	      display: grid;
	      grid-template-columns: 1fr;
	      gap: 10px;
	    }
	    .compare-card {
	      border: 1px solid var(--soft-line);
	      border-radius: 8px;
	      padding: 13px;
	      background: #fbfcfe;
	    }
	    .compare-card strong {
	      display: block;
	      margin-bottom: 8px;
	      font-size: 14px;
	    }
	    .compare-card p {
	      margin: 8px 0 0;
	      color: var(--muted);
	      line-height: 1.45;
	    }
	    .compare-card--lesson {
	      border-color: #bfdbfe;
	      background: #eff6ff;
	    }
	    .mini-hairball {
	      position: relative;
	      height: 86px;
	      border: 1px dashed #cbd5e1;
	      border-radius: 8px;
	      background:
	        linear-gradient(35deg, transparent 46%, #cbd5e1 47%, #cbd5e1 48%, transparent 49%),
	        linear-gradient(145deg, transparent 46%, #cbd5e1 47%, #cbd5e1 48%, transparent 49%),
	        #fff;
	      overflow: hidden;
	    }
	    .mini-hairball span {
	      position: absolute;
	      width: 9px;
	      height: 9px;
	      border-radius: 50%;
	      background: #94a3b8;
	    }
	    .mini-hairball span:nth-child(1) { left: 14%; top: 22%; }
	    .mini-hairball span:nth-child(2) { left: 31%; top: 67%; }
	    .mini-hairball span:nth-child(3) { left: 52%; top: 34%; }
	    .mini-hairball span:nth-child(4) { left: 73%; top: 58%; }
	    .mini-hairball span:nth-child(5) { left: 84%; top: 20%; }
	    .mini-path {
	      display: grid;
	      gap: 8px;
	      margin: 0;
	      padding: 0;
	      list-style: none;
	    }
	    .mini-path li {
	      display: grid;
	      grid-template-columns: 22px minmax(0, 1fr);
	      gap: 8px;
	      align-items: center;
	      color: var(--ink);
	      font-size: 13px;
	    }
	    .mini-path span {
	      display: inline-grid;
	      place-items: center;
	      width: 22px;
	      height: 22px;
	      border-radius: 50%;
	      background: var(--accent);
	      color: #fff;
	      font-size: 11px;
	      font-weight: 750;
	    }
	    .reader-grid {
	      display: grid;
	      grid-template-columns: minmax(180px, 230px) minmax(0, 1fr) minmax(240px, 300px);
	      gap: 18px;
	      align-items: start;
	    }
	    .lesson-nav, .lesson-side, .lesson-card, .context-section, .reference-card {
	      background: var(--panel);
	      border: 1px solid var(--line);
	      border-radius: 8px;
	      box-shadow: var(--shadow);
	    }
	    .lesson-nav, .lesson-side {
	      position: sticky;
	      top: 18px;
	      padding: 14px;
	    }
	    .lesson-nav a {
	      display: block;
	      margin-top: 10px;
	      color: var(--ink);
	      text-decoration: none;
	      font-size: 13px;
	      line-height: 1.35;
	      border-left: 3px solid var(--soft-line);
	      padding: 5px 0 5px 10px;
	    }
	    .lesson-nav a:hover, .lesson-nav a:focus {
	      border-left-color: var(--accent);
	      color: var(--accent);
	      outline: none;
	    }
	    .lesson-reader {
	      display: grid;
	      gap: 16px;
	    }
	    .lesson-card {
	      padding: 18px;
	    }
	    .lesson-card h3, .lesson-side h3 {
	      margin: 0 0 8px;
	      font-size: 16px;
	    }
    .goal-list, .chapter-list, .lesson-steps {
      display: grid;
      gap: 10px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .goal-list li {
      padding-left: 12px;
      border-left: 3px solid var(--accent);
      color: var(--muted);
      line-height: 1.5;
    }
    .lesson-step {
      display: grid;
      grid-template-columns: 30px minmax(0, 1fr);
      gap: 10px;
      align-items: start;
      padding: 10px 0;
      border-top: 1px solid var(--soft-line);
    }
    .lesson-step:first-child {
      border-top: 0;
      padding-top: 0;
    }
    .lesson-step-body {
      display: grid;
      gap: 6px;
      min-width: 0;
    }
    .lesson-step-head {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .evidence-tag {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      background: #fff;
      color: var(--muted);
      font-size: 12px;
    }
    .guide-jump {
      justify-self: start;
      border: 1px solid var(--accent);
      border-radius: 6px;
      padding: 6px 9px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .guide-jump:hover, .guide-jump:focus {
      background: #dbeafe;
      outline: none;
    }
	    .chapter-list li {
	      border-top: 1px solid var(--soft-line);
	      padding-top: 10px;
	    }
    .chapter-list li:first-child {
      border-top: 0;
      padding-top: 0;
    }
	    .chapter-title {
	      display: block;
	      color: var(--ink);
	      font-weight: 750;
	      margin-bottom: 4px;
	    }
	    .context-section {
	      padding: 18px;
	    }
	    .reference-section {
	      display: grid;
	      gap: 16px;
	      padding-top: 8px;
	    }
	    .section-intro {
	      display: grid;
	      gap: 7px;
	      max-width: 780px;
	    }
	    .reference-layout {
	      display: grid;
	      grid-template-columns: minmax(240px, 320px) minmax(0, 1fr);
	      gap: 18px;
	      align-items: start;
	    }
	    .module-index {
	      position: sticky;
	      top: 18px;
	      max-height: calc(100vh - 36px);
	      overflow: auto;
	      padding: 14px;
	      background: var(--panel);
	      border: 1px solid var(--line);
	      border-radius: 8px;
	      box-shadow: var(--shadow);
	    }
	    .module-index h2 {
	      margin-bottom: 10px;
	    }
	    .reference-stack {
	      display: grid;
	      gap: 18px;
	    }
	    .reference-card {
	      padding: 18px;
	    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 6px;
      max-width: 70%;
    }
    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: var(--muted);
      font-size: 12px;
      border: 1px solid var(--soft-line);
      border-radius: 999px;
      padding: 3px 8px;
      background: #fbfcfe;
    }
    .legend-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--module);
    }
    .detail-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(220px, 320px);
      gap: 16px;
    }
    .summary {
      color: var(--muted);
      line-height: 1.6;
      margin: 0;
    }
    .detail-stack {
      display: grid;
      gap: 12px;
    }
    .insight-card {
      border: 1px solid var(--soft-line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfe;
    }
    .insight-card h3 {
      margin: 0 0 7px;
      font-size: 13px;
      color: var(--ink);
    }
    .signal-list, .metric-list, .relation-list {
      display: grid;
      gap: 7px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .signal-list li, .metric-list li {
      color: var(--muted);
      line-height: 1.45;
      overflow-wrap: anywhere;
    }
    .relation-button {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 7px 9px;
      background: #fff;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
      overflow-wrap: anywhere;
    }
    .relation-button:hover, .relation-button:focus {
      border-color: var(--accent);
      outline: none;
      background: var(--accent-soft);
    }
    code {
      display: inline-block;
      max-width: 100%;
      overflow-wrap: anywhere;
      color: #334155;
      background: #eef2f7;
      border-radius: 4px;
      padding: 2px 5px;
      font-size: 13px;
    }
    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }
    .pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 9px;
      color: var(--muted);
      font-size: 12px;
      background: #fff;
    }
    .graph {
      width: 100%;
      min-height: 420px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
      overflow: auto;
    }
    svg {
      display: block;
      width: 100%;
      min-width: 760px;
      height: 520px;
    }
    .lane {
      fill: #f8fafc;
      stroke: #e2e8f0;
      stroke-width: 1;
    }
    .lane-label {
      fill: #64748b;
      font-size: 12px;
      font-weight: 700;
    }
    .edge {
      fill: none;
      stroke: #94a3b8;
      stroke-width: 1.6;
    }
    .edge-label-bg {
      fill: #fbfcfe;
      stroke: #e2e8f0;
      stroke-width: 1;
      rx: 4;
    }
    .edge-label {
      fill: var(--muted);
      font-size: 11px;
    }
    .node-rect {
      fill: #ffffff;
      stroke: #b9c3d1;
      stroke-width: 1.2;
      rx: 7;
    }
    .node-rect.active {
      fill: var(--accent-soft);
      stroke: var(--accent);
      stroke-width: 2;
    }
    .node-stripe {
      rx: 7;
    }
    .node-text {
      fill: var(--ink);
      font-size: 13px;
      font-weight: 650;
    }
    .node-kind {
      fill: var(--muted);
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .flow-list, .evidence-list, .question-list {
      display: grid;
      gap: 10px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .flow, .evidence, .question {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
    }
    .flow h3 {
      margin: 0 0 6px;
      font-size: 15px;
    }
    .steps {
      margin-top: 10px;
      display: grid;
      gap: 8px;
    }
    .step {
      display: grid;
      grid-template-columns: 28px minmax(0, 1fr);
      gap: 8px;
      align-items: start;
    }
    .step-index {
      display: inline-grid;
      place-items: center;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      color: #fff;
      background: var(--accent);
      font-size: 12px;
      font-weight: 750;
    }
    .step-body {
      display: grid;
      gap: 4px;
      padding-left: 10px;
      border-left: 3px solid var(--accent);
    }
    .muted {
      color: var(--muted);
      line-height: 1.5;
    }
	    @media (max-width: 860px) {
	      .guide-hero, .reader-grid, .reference-layout {
	        grid-template-columns: 1fr;
	      }
	      .lesson-nav, .lesson-side, .module-index {
	        position: static;
	        max-height: none;
	      }
	      .detail-grid {
	        grid-template-columns: 1fr;
	      }
	      .legend {
	        max-width: 100%;
	        justify-content: flex-start;
      }
      .section-head {
        display: grid;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>__TITLE__</h1>
    <p>__SUMMARY__</p>
  </header>
	  <main>
	    <div class="workspace">
	      <section id="guideSection" class="guide-section" hidden>
	        <div id="guide"></div>
	      </section>
	      <section id="selectedModuleSection" class="context-section">
	        <h2 id="selectedModuleTitle"></h2>
	        <div id="details" class="detail-grid"></div>
	      </section>
	      <section id="referenceSection" class="reference-section">
	        <div class="section-intro">
	          <span class="guide-kicker" id="referenceKicker"></span>
	          <h2 id="referenceIndexTitle"></h2>
	          <p id="referenceIntro" class="summary"></p>
	        </div>
	        <div class="reference-layout">
	          <aside class="module-index">
	            <h2 id="moduleIndexTitle"></h2>
	            <label id="searchLabel" class="sr-only" for="search"></label>
	            <input id="search" class="search" type="search">
	            <div id="stats" class="stats"></div>
	            <div id="nodeList" class="node-list"></div>
	          </aside>
	          <div class="reference-stack">
	            <div id="moduleMapSection" class="reference-card">
	              <div class="section-head">
	                <h2 id="moduleMapTitle"></h2>
	                <div id="legend" class="legend"></div>
	              </div>
	              <div class="graph"><svg id="graph" role="img"></svg></div>
	            </div>
	          </div>
	        </div>
	      </section>
	      <section>
	        <h2 id="coreFlowsTitle"></h2>
	        <ul id="flows" class="flow-list"></ul>
      </section>
      <section>
        <h2 id="evidenceTitle"></h2>
        <ul id="evidence" class="evidence-list"></ul>
      </section>
      <section>
        <h2 id="openQuestionsTitle"></h2>
        <ul id="questions" class="question-list"></ul>
      </section>
    </div>
  </main>
  <script id="graph-data" type="application/json">__DATA_JSON__</script>
  <script>
    const data = JSON.parse(document.getElementById('graph-data').textContent);
    const labels = data.labels || {};
    const kindLabels = labels.kindLabels || {};
    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
    const edges = Array.isArray(data.edges) ? data.edges : [];
    const flows = Array.isArray(data.flows) ? data.flows : [];
	    const evidence = Array.isArray(data.evidence) ? data.evidence : [];
	    const questions = Array.isArray(data.questions) ? data.questions : [];
	    const guide = data.guide && typeof data.guide === 'object' ? data.guide : null;
	    let selectedId = guide?.quickstart?.start_node || nodes[0]?.id || null;
	    document.body.classList.toggle('has-guide', Boolean(guide));

    const nodeList = document.getElementById('nodeList');
    const search = document.getElementById('search');
    const details = document.getElementById('details');
    const svg = document.getElementById('graph');
    const guideSection = document.getElementById('guideSection');
    const guideRoot = document.getElementById('guide');

    const colorMap = {
      skill: '#0e7490',
      entrypoint: '#7c3aed',
      module: '#2563eb',
      script: '#d97706',
      external: '#059669',
      data: '#be123c',
      test: '#64748b',
      config: '#475569',
      document: '#a16207'
    };

    function l(key, fallback = '') {
      return labels[key] || fallback || key;
    }

    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
      }[ch]));
    }

    function normalizeKind(kind) {
      const raw = String(kind || '').toLowerCase();
      if (raw.includes('skill') || raw.includes('技能')) return 'skill';
      if (raw.includes('entry') || raw.includes('入口')) return 'entrypoint';
      if (raw.includes('script') || raw.includes('脚本')) return 'script';
      if (raw.includes('external') || raw.includes('tool') || raw.includes('api') || raw.includes('外部')) return 'external';
      if (raw.includes('data') || raw.includes('store') || raw.includes('数据')) return 'data';
      if (raw.includes('test') || raw.includes('测试')) return 'test';
      if (raw.includes('config') || raw.includes('配置')) return 'config';
      if (raw.includes('doc') || raw.includes('文档')) return 'document';
      return 'module';
    }

    function colorFor(nodeOrKind) {
      const kind = typeof nodeOrKind === 'string' ? nodeOrKind : nodeOrKind?.kind;
      return colorMap[normalizeKind(kind)] || colorMap.module;
    }

    function displayKind(kind) {
      if (!kind) return l('moduleKind');
      return kindLabels[kind] || kindLabels[normalizeKind(kind)] || kind;
    }

    function labelFor(id) {
      return nodes.find(n => n.id === id)?.label || id;
    }

    function groupFor(node) {
      return node.group || node.layer || displayKind(node.kind) || l('defaultGroup');
    }

    function filteredNodes() {
      const q = search.value.trim().toLowerCase();
      if (!q) return nodes;
      return nodes.filter(n =>
        [
          n.label,
          n.kind,
          n.path,
          n.summary,
          n.meaning,
          n.next_read,
          Array.isArray(n.signals) ? n.signals.join(' ') : '',
          n.metrics && typeof n.metrics === 'object' ? JSON.stringify(n.metrics) : '',
          groupFor(n)
        ].some(v => String(v || '').toLowerCase().includes(q))
      );
    }

    function renderStaticLabels() {
	      document.getElementById('searchLabel').textContent = l('filterModules');
	      search.placeholder = l('filterModules');
	      search.setAttribute('aria-label', l('filterModules'));
	      document.getElementById('referenceKicker').textContent = l('referenceIndexTitle');
	      document.getElementById('referenceIndexTitle').textContent = l('referenceIndexTitle');
	      document.getElementById('referenceIntro').textContent = l('referenceIndexIntro');
	      document.getElementById('moduleIndexTitle').textContent = l('moduleIndexTitle');
	      document.getElementById('moduleMapTitle').textContent = l('moduleMap');
      document.getElementById('selectedModuleTitle').textContent = l('selectedModule');
      document.getElementById('coreFlowsTitle').textContent = l('coreFlows');
      document.getElementById('evidenceTitle').textContent = l('evidence');
      document.getElementById('openQuestionsTitle').textContent = l('openQuestions');
      svg.setAttribute('aria-label', l('graphAria'));
    }

    function renderStats() {
      const stats = document.getElementById('stats');
      stats.innerHTML = `
        <span class="stat">${nodes.length} ${esc(l('modules', 'modules'))}</span>
        <span class="stat">${edges.length} ${esc(l('relations', 'relations'))}</span>
      `;
    }

    function renderLegend() {
      const legend = document.getElementById('legend');
      const kinds = [];
      for (const node of nodes) {
        const normalized = normalizeKind(node.kind);
        if (!kinds.includes(normalized)) kinds.push(normalized);
      }
      legend.innerHTML = kinds.map(kind => `
        <span class="legend-item">
          <span class="legend-dot" style="background:${colorFor(kind)}"></span>
          ${esc(displayKind(kind))}
        </span>
      `).join('');
    }

    function renderNodeList() {
      nodeList.innerHTML = '';
      for (const node of filteredNodes()) {
        const button = document.createElement('button');
        button.className = 'node';
        button.type = 'button';
        button.setAttribute('aria-selected', String(node.id === selectedId));
        button.innerHTML = `
          <span class="node-swatch" style="background:${colorFor(node)}"></span>
          <span class="node-copy">
            <span class="kind">${esc(displayKind(node.kind))}</span>
            <span class="label">${esc(node.label || node.id)}</span>
            ${node.path ? `<span class="node-path">${esc(node.path)}</span>` : ''}
          </span>
        `;
        button.addEventListener('click', () => {
          selectedId = node.id;
          render();
        });
        nodeList.appendChild(button);
      }
    }

    function renderList(items, emptyText) {
      if (!Array.isArray(items) || !items.length) return `<li class="muted">${esc(emptyText)}</li>`;
      return items.map(item => `<li>${esc(item)}</li>`).join('');
    }

	    function renderGuideStep(step, index) {
	      const node = step.node && nodes.some(item => item.id === step.node) ? step.node : '';
	      return `
	        <li class="lesson-step">
          <span class="step-index">${index + 1}</span>
          <span class="lesson-step-body">
            <span class="lesson-step-head">
              <strong>${esc(step.label || l('stepFallback'))}</strong>
              ${step.evidence_type ? `<span class="evidence-tag">${esc(l('evidenceTypeTitle'))}: ${esc(step.evidence_type)}</span>` : ''}
            </span>
            ${step.summary ? `<span class="muted">${esc(step.summary)}</span>` : ''}
            ${step.takeaway ? `<span class="muted"><strong>${esc(l('takeawayTitle'))}:</strong> ${esc(step.takeaway)}</span>` : ''}
            ${step.evidence ? `<span class="muted">${esc(step.evidence)}</span>` : ''}
            ${step.path ? `<code>${esc(step.path)}</code>` : ''}
            ${node ? `<button type="button" class="guide-jump" data-guide-node="${esc(node)}">${esc(l('viewModule'))}</button>` : ''}
          </span>
	        </li>
	      `;
	    }

	    function renderChapterCard(chapter, index) {
	      const steps = Array.isArray(chapter.steps) ? chapter.steps : [];
	      return `
	        <article id="lesson-chapter-${index + 1}" class="lesson-card">
	          <span class="guide-kicker">${esc(l('chaptersNavTitle'))} ${index + 1}</span>
	          <h3>${esc(chapter.title || `${l('chaptersTitle')} ${index + 1}`)}</h3>
	          ${chapter.question ? `<p class="summary"><strong>${esc(l('guidingQuestionTitle'))}:</strong> ${esc(chapter.question)}</p>` : ''}
	          ${chapter.summary ? `<p class="summary">${esc(chapter.summary)}</p>` : ''}
	          ${chapter.principle ? `<p class="summary"><strong>${esc(l('principleTitle'))}:</strong> ${esc(chapter.principle)}</p>` : ''}
	          <ol class="lesson-steps">${steps.map((step, stepIndex) => renderGuideStep(step, stepIndex)).join('')}</ol>
	        </article>
	      `;
	    }

	    function renderEvidenceNotes(items) {
	      if (!Array.isArray(items) || !items.length) {
	        return `<li class="muted">${esc(l('noEvidence'))}</li>`;
	      }
	      return items.map(item => `
	        <li>
	          <strong>${esc(item.type || l('evidenceFallback'))}</strong>
	          ${item.path ? `<code>${esc(item.path)}</code>` : ''}
	          ${item.detail ? `<span class="muted">${esc(item.detail)}</span>` : ''}
	        </li>
	      `).join('');
	    }

	    function renderGuide() {
	      if (!guide) {
	        guideSection.hidden = true;
	        return;
      }
      guideSection.hidden = false;
      const quickstart = guide.quickstart || {};
	      const caseStudy = guide.case_study || {};
	      const goals = Array.isArray(quickstart.learning_goals) ? quickstart.learning_goals : [];
	      const caseSteps = Array.isArray(caseStudy.steps) ? caseStudy.steps : [];
	      const chapters = Array.isArray(guide.chapters) ? guide.chapters : [];
	      const evidenceNotes = Array.isArray(guide.evidence) ? guide.evidence : [];
	      const previewSteps = caseSteps.slice(0, 4);
	      guideRoot.innerHTML = `
	        <div class="guide-shell">
	          <div class="guide-hero">
	            <div class="guide-hero-copy">
	              <span class="guide-kicker">${esc(l('readerModeTitle'))}</span>
	              <h2 class="guide-title">${esc(quickstart.title || data.title || l('quickstartTitle'))}</h2>
	              <p class="summary">${esc(quickstart.problem || data.summary || l('noGuide'))}</p>
	              ${quickstart.why_this_path ? `
	                <div>
	                  <strong>${esc(l('whyThisPathTitle'))}</strong>
	                  <p class="summary">${esc(quickstart.why_this_path)}</p>
	                </div>
	              ` : ''}
	              <div class="pill-row">
	                ${quickstart.project_types ? `<span class="pill">${esc(l('projectTypesTitle'))}: ${esc(quickstart.project_types)}</span>` : ''}
	                ${quickstart.start_path ? `<span class="pill">${esc(l('pathLabel'))}: <code>${esc(quickstart.start_path)}</code></span>` : ''}
	              </div>
	            </div>
	            <div class="problem-compare">
	              <div class="compare-card">
	                <strong>${esc(l('mapFirstTitle'))}</strong>
	                <div class="mini-hairball" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
	                <p>${nodes.length} ${esc(l('modules', 'modules'))}. ${edges.length} ${esc(l('relations', 'relations'))}. ${esc(l('mapFirstCaption'))}</p>
	              </div>
	              <div class="compare-card compare-card--lesson">
	                <strong>${esc(l('lessonFirstTitle'))}</strong>
	                <ol class="mini-path">
	                  ${previewSteps.map((step, index) => `<li><span>${index + 1}</span>${esc(step.label || l('stepFallback'))}</li>`).join('')}
	                </ol>
	                <p>${esc(l('lessonFirstCaption'))}</p>
	              </div>
	            </div>
	          </div>
	          <div class="reader-grid">
	            <nav class="lesson-nav" aria-label="${esc(l('studyPathTitle'))}">
	              <span class="guide-kicker">${esc(l('studyPathTitle'))}</span>
	              <a href="#lesson-case">${esc(l('caseStudyTitle'))}: ${esc(caseStudy.title || l('casePathTitle'))}</a>
	              ${chapters.map((chapter, index) => `<a href="#lesson-chapter-${index + 1}">${esc(chapter.title || `${l('chaptersTitle')} ${index + 1}`)}</a>`).join('')}
	              <a href="#referenceSection">${esc(l('referenceIndexTitle'))}</a>
	            </nav>
	            <div class="lesson-reader">
	              <article id="lesson-case" class="lesson-card">
	                <span class="guide-kicker">${esc(l('casePathTitle'))}</span>
	                <h3>${esc(caseStudy.title || l('caseStudyTitle'))}</h3>
	                ${caseStudy.trigger ? `<p class="summary">${esc(caseStudy.trigger)}</p>` : ''}
	                ${caseStudy.mental_model ? `<p class="summary">${esc(caseStudy.mental_model)}</p>` : ''}
	                <ol class="lesson-steps">${caseSteps.map((step, index) => renderGuideStep(step, index)).join('')}</ol>
	              </article>
	              ${chapters.map((chapter, index) => renderChapterCard(chapter, index)).join('')}
	            </div>
	            <aside class="lesson-side">
	              <h3>${esc(l('learningGoalsTitle'))}</h3>
	              <ul class="goal-list">${renderList(goals, l('noGuide'))}</ul>
	              <h3 style="margin-top:16px">${esc(l('evidenceTypeTitle'))}</h3>
	              <ul class="goal-list">${renderEvidenceNotes(evidenceNotes)}</ul>
	            </aside>
	          </div>
	        </div>
	      `;
      guideRoot.querySelectorAll('[data-guide-node]').forEach(button => {
        button.addEventListener('click', () => {
          selectedId = button.getAttribute('data-guide-node');
          render();
          document.getElementById('selectedModuleSection')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
      });
    }

    function renderMetrics(metrics) {
      if (!metrics || typeof metrics !== 'object') return `<li class="muted">${esc(l('noMetrics'))}</li>`;
      const entries = Object.entries(metrics).filter(([, value]) => value !== null && value !== undefined && value !== '');
      if (!entries.length) return `<li class="muted">${esc(l('noMetrics'))}</li>`;
      return entries.map(([key, value]) => `<li><strong>${esc(key)}:</strong> ${esc(value)}</li>`).join('');
    }

    function renderRelationButtons(relations, direction) {
      if (!relations.length) return `<li class="muted">${esc(l('noneListed'))}</li>`;
      return relations.map(edge => {
        const otherId = direction === 'incoming' ? edge.from : edge.to;
        const edgeLabel = edge.label || edge.kind || l('edgeFallback');
        return `
          <li>
            <button type="button" class="relation-button" data-node-id="${esc(otherId)}">
              <strong>${esc(labelFor(otherId))}</strong>
              <span class="muted">${esc(edgeLabel)}</span>
            </button>
          </li>
        `;
      }).join('');
    }

    function attachRelationHandlers() {
      details.querySelectorAll('[data-node-id]').forEach(button => {
        button.addEventListener('click', () => {
          selectedId = button.getAttribute('data-node-id');
          render();
        });
      });
    }

    function renderDetails() {
      const node = nodes.find(n => n.id === selectedId) || nodes[0] || {};
      const outgoing = edges.filter(e => e.from === node.id);
      const incoming = edges.filter(e => e.to === node.id);
      const meaning = node.meaning || node.summary || l('noSummary');
      const nextRead = node.next_read || '';
      details.innerHTML = `
        <div class="detail-stack">
          <div class="insight-card">
            <h3>${esc(l('meaningTitle'))}</h3>
            <p class="summary">${esc(meaning)}</p>
          </div>
          ${nextRead ? `
            <div class="insight-card">
              <h3>${esc(l('nextReadTitle'))}</h3>
              <p class="summary">${esc(nextRead)}</p>
            </div>
          ` : ''}
          <div class="pill-row">
            <span class="pill">${esc(displayKind(node.kind))}</span>
            <span class="pill">${esc(l('groupLabel'))}: ${esc(groupFor(node))}</span>
            ${node.path ? `<span class="pill">${esc(l('pathLabel'))}: <code>${esc(node.path)}</code></span>` : ''}
          </div>
        </div>
        <div class="detail-stack">
          <div class="insight-card">
            <h3>${esc(l('relationsTitle'))}</h3>
            <div class="muted"><strong>${esc(l('incoming'))}</strong></div>
            <ul class="relation-list">${renderRelationButtons(incoming, 'incoming')}</ul>
            <div class="muted" style="margin-top:10px"><strong>${esc(l('outgoing'))}</strong></div>
            <ul class="relation-list">${renderRelationButtons(outgoing, 'outgoing')}</ul>
          </div>
          <div class="insight-card">
            <h3>${esc(l('signalsTitle'))}</h3>
            <ul class="signal-list">${renderList(node.signals, l('noSignals'))}</ul>
          </div>
          <div class="insight-card">
            <h3>${esc(l('metricsTitle'))}</h3>
            <ul class="metric-list">${renderMetrics(node.metrics)}</ul>
          </div>
        </div>
      `;
      attachRelationHandlers();
    }

    function wrapLabel(text, max = 16) {
      const raw = String(text || '').trim();
      if (!raw) return [];
      const tokens = raw.includes(' ')
        ? raw.split(/\\s+/)
        : raw.split(/(?=[/._-])|(?<=[/._-])/).filter(Boolean);
      const pieces = [];
      for (const token of tokens) {
        if (token.length <= max) {
          pieces.push(token);
          continue;
        }
        for (let i = 0; i < token.length; i += max) pieces.push(token.slice(i, i + max));
      }
      const lines = [];
      let line = '';
      for (const piece of pieces) {
        const next = raw.includes(' ') ? `${line} ${piece}`.trim() : `${line}${piece}`;
        if (next.length > max && line) {
          lines.push(line);
          line = piece;
        } else {
          line = next;
        }
      }
      if (line) lines.push(line);
      return lines.slice(0, 3);
    }

    function computeLevels() {
      const outgoing = new Map(nodes.map(node => [node.id, []]));
      const incoming = new Map(nodes.map(node => [node.id, 0]));
      for (const edge of edges) {
        if (!outgoing.has(edge.from) || !incoming.has(edge.to)) continue;
        outgoing.get(edge.from).push(edge.to);
        incoming.set(edge.to, incoming.get(edge.to) + 1);
      }
      const roots = nodes.filter(node => (incoming.get(node.id) || 0) === 0);
      const queue = roots.length ? roots.map(node => node.id) : nodes.slice(0, 1).map(node => node.id);
      const levels = new Map(queue.map(id => [id, 0]));
      let guard = 0;
      while (queue.length && guard < nodes.length * Math.max(1, edges.length + 1)) {
        guard += 1;
        const id = queue.shift();
        const nextLevel = (levels.get(id) || 0) + 1;
        for (const to of outgoing.get(id) || []) {
          if (!levels.has(to) || nextLevel > levels.get(to)) {
            levels.set(to, nextLevel);
            queue.push(to);
          }
        }
      }
      let fallbackLevel = Math.max(0, ...levels.values()) + 1;
      for (const node of nodes) {
        if (!levels.has(node.id)) {
          levels.set(node.id, fallbackLevel);
          fallbackLevel += 1;
        }
      }
      return levels;
    }

    function buildLayout() {
      const levels = computeLevels();
      const groups = [];
      const byGroupAndLevel = new Map();
      for (const node of nodes) {
        const group = groupFor(node);
        if (!groups.includes(group)) groups.push(group);
        const key = `${group}::${levels.get(node.id) || 0}`;
        if (!byGroupAndLevel.has(key)) byGroupAndLevel.set(key, []);
        byGroupAndLevel.get(key).push(node);
      }

      const nodeWidth = 170;
      const nodeHeight = 66;
      const laneLeft = 22;
      const laneLabelWidth = 88;
      const laneTopPad = 36;
      const laneGap = 20;
      const colGap = 96;
      const rowGap = 16;
      const maxLevel = Math.max(0, ...Array.from(levels.values()));
      const groupHeights = new Map();
      for (const group of groups) {
        let maxStack = 1;
        for (let level = 0; level <= maxLevel; level += 1) {
          maxStack = Math.max(maxStack, (byGroupAndLevel.get(`${group}::${level}`) || []).length);
        }
        groupHeights.set(group, Math.max(124, laneTopPad + maxStack * nodeHeight + (maxStack - 1) * rowGap + 28));
      }

      const laneY = new Map();
      let yCursor = 18;
      for (const group of groups) {
        laneY.set(group, yCursor);
        yCursor += groupHeights.get(group) + laneGap;
      }

      const positions = new Map();
      for (const group of groups) {
        for (let level = 0; level <= maxLevel; level += 1) {
          const stack = byGroupAndLevel.get(`${group}::${level}`) || [];
          stack.forEach((node, index) => {
            positions.set(node.id, {
              x: laneLeft + laneLabelWidth + level * (nodeWidth + colGap),
              y: laneY.get(group) + laneTopPad + index * (nodeHeight + rowGap),
              width: nodeWidth,
              height: nodeHeight
            });
          });
        }
      }

      const width = Math.max(820, laneLeft + laneLabelWidth + (maxLevel + 1) * nodeWidth + maxLevel * colGap + 50);
      const height = Math.max(420, yCursor + 8);
      return { positions, groups, groupHeights, laneY, width, height, nodeWidth, nodeHeight };
    }

    function createSvgElement(name, attrs = {}) {
      const el = document.createElementNS('http://www.w3.org/2000/svg', name);
      for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
      return el;
    }

    function renderGraph() {
      const layout = buildLayout();
      svg.setAttribute('viewBox', `0 0 ${layout.width} ${layout.height}`);
      svg.style.height = `${layout.height}px`;
      svg.innerHTML = '';

      const defs = createSvgElement('defs');
      defs.innerHTML = '<marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#94a3b8"></path></marker>';
      svg.appendChild(defs);

      for (const group of layout.groups) {
        const y = layout.laneY.get(group);
        svg.appendChild(createSvgElement('rect', {
          x: 12,
          y,
          width: layout.width - 24,
          height: layout.groupHeights.get(group),
          class: 'lane',
          rx: 8
        }));
        const text = createSvgElement('text', {
          x: 28,
          y: y + 25,
          class: 'lane-label'
        });
        text.textContent = group;
        svg.appendChild(text);
      }

      for (const edge of edges) {
        const from = layout.positions.get(edge.from);
        const to = layout.positions.get(edge.to);
        if (!from || !to) continue;
        const x1 = from.x + from.width;
        const y1 = from.y + from.height / 2;
        const x2 = to.x;
        const y2 = to.y + to.height / 2;
        const curve = Math.max(42, Math.min(100, Math.abs(x2 - x1) / 2));
        const path = createSvgElement('path', {
          d: `M ${x1} ${y1} C ${x1 + curve} ${y1}, ${x2 - curve} ${y2}, ${x2} ${y2}`,
          class: 'edge',
          'marker-end': 'url(#arrow)'
        });
        svg.appendChild(path);
        const edgeLabel = edge.label || edge.kind;
        if (edgeLabel) {
          const tx = (x1 + x2) / 2;
          const ty = (y1 + y2) / 2 - 7;
          const textValue = String(edgeLabel);
          const bg = createSvgElement('rect', {
            x: tx - Math.max(28, textValue.length * 3.4),
            y: ty - 13,
            width: Math.max(56, textValue.length * 6.8),
            height: 18,
            class: 'edge-label-bg'
          });
          svg.appendChild(bg);
          const label = createSvgElement('text', {
            x: tx,
            y: ty,
            class: 'edge-label',
            'text-anchor': 'middle'
          });
          label.textContent = textValue;
          svg.appendChild(label);
        }
      }

      for (const node of nodes) {
        const pos = layout.positions.get(node.id);
        if (!pos) continue;
        const group = createSvgElement('g', {
          tabindex: '0',
          role: 'button',
          'aria-label': node.label || node.id
        });
        group.style.cursor = 'pointer';
        group.addEventListener('click', () => {
          selectedId = node.id;
          render();
        });
        group.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            selectedId = node.id;
            render();
          }
        });
        group.appendChild(createSvgElement('rect', {
          x: pos.x,
          y: pos.y,
          width: pos.width,
          height: pos.height,
          class: `node-rect${node.id === selectedId ? ' active' : ''}`
        }));
        group.appendChild(createSvgElement('rect', {
          x: pos.x,
          y: pos.y,
          width: 7,
          height: pos.height,
          class: 'node-stripe',
          fill: colorFor(node)
        }));
        const kind = createSvgElement('text', {
          x: pos.x + 14,
          y: pos.y + 18,
          class: 'node-kind'
        });
        kind.textContent = displayKind(node.kind);
        group.appendChild(kind);
        wrapLabel(node.label || node.id).forEach((lineText, lineIndex) => {
          const text = createSvgElement('text', {
            x: pos.x + 14,
            y: pos.y + 38 + lineIndex * 15,
            class: 'node-text'
          });
          text.textContent = lineText;
          group.appendChild(text);
        });
        svg.appendChild(group);
      }
    }

    function renderFlows() {
      const list = document.getElementById('flows');
      list.innerHTML = flows.length ? '' : `<li class="flow muted">${esc(l('noFlows'))}</li>`;
      for (const flow of flows) {
        const item = document.createElement('li');
        item.className = 'flow';
        const steps = Array.isArray(flow.steps) ? flow.steps : [];
        item.innerHTML = `
          <h3>${esc(flow.name || l('flowFallback'))}</h3>
          <div class="muted">${esc(flow.summary || '')}</div>
          <div class="steps">
            ${steps.map((step, index) => `
              <div class="step">
                <span class="step-index">${index + 1}</span>
                <span class="step-body">
                  <strong>${esc(step.label || step.node || l('stepFallback'))}</strong>
                  ${step.node ? `<span class="muted">${esc(labelFor(step.node))}</span>` : ''}
                  ${step.summary ? `<span class="muted">${esc(step.summary)}</span>` : ''}
                  ${step.path ? `<code>${esc(step.path)}</code>` : ''}
                </span>
              </div>
            `).join('')}
          </div>
        `;
        list.appendChild(item);
      }
    }

    function renderEvidence() {
      const list = document.getElementById('evidence');
      list.innerHTML = evidence.length ? '' : `<li class="evidence muted">${esc(l('noEvidence'))}</li>`;
      for (const entry of evidence) {
        const item = document.createElement('li');
        item.className = 'evidence';
        item.innerHTML = `<strong>${esc(entry.claim || l('evidenceFallback'))}</strong><div class="muted">${esc(entry.detail || '')}</div>${entry.path ? `<code>${esc(entry.path)}</code>` : ''}`;
        list.appendChild(item);
      }
    }

    function renderQuestions() {
      const list = document.getElementById('questions');
      list.innerHTML = questions.length ? '' : `<li class="question muted">${esc(l('noQuestions'))}</li>`;
      for (const question of questions) {
        const item = document.createElement('li');
        item.className = 'question';
        item.textContent = String(question);
        list.appendChild(item);
      }
    }

    function render() {
      renderGuide();
      renderNodeList();
      renderDetails();
      renderGraph();
      renderFlows();
      renderEvidence();
      renderQuestions();
    }

    renderStaticLabels();
    renderStats();
    renderLegend();
    search.addEventListener('input', renderNodeList);
    render();
  </script>
</body>
</html>
"""


def contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def infer_locale(data: dict[str, Any], override: str | None = None) -> str:
    if override:
        return override
    locale = str(data.get("locale") or "").strip()
    if locale:
        return locale
    text = " ".join(
        str(value)
        for value in (
            data.get("title"),
            data.get("summary"),
            " ".join(str(node.get("label", "")) for node in data.get("nodes", [])),
            " ".join(str(flow.get("name", "")) for flow in data.get("flows", [])),
        )
    )
    return "zh-CN" if contains_cjk(text) else "en"


def build_render_data(data: dict[str, Any], locale_override: str | None = None) -> tuple[str, dict[str, Any]]:
    locale = infer_locale(data, locale_override)
    base_labels = LABELS_ZH if locale.lower().startswith("zh") else LABELS_EN
    user_labels = data.get("labels") if isinstance(data.get("labels"), dict) else {}
    render_data = deepcopy(data)
    render_data["locale"] = locale
    render_data["labels"] = merge_dicts(base_labels, user_labels)
    return locale, render_data


def script_safe_json(data: dict[str, Any]) -> str:
    text = json.dumps(data, ensure_ascii=False)
    return (
        text.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def validate_graph(data: dict[str, Any]) -> None:
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        raise SystemExit("understanding_graph.json field 'nodes' must be a list")
    node_ids = [node.get("id") for node in nodes if isinstance(node, dict) and node.get("id")]
    if not node_ids:
        raise SystemExit("understanding_graph.json must contain at least one node with an id")
    duplicates = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate node ids: {', '.join(duplicates)}")

    known = set(node_ids)
    edges = data.get("edges", [])
    if not isinstance(edges, list):
        raise SystemExit("understanding_graph.json field 'edges' must be a list")
    for edge in edges:
        if not isinstance(edge, dict):
            raise SystemExit("Each edge must be an object")
        if edge.get("from") not in known:
            raise SystemExit(f"Edge references unknown from node: {edge.get('from')}")
        if edge.get("to") not in known:
            raise SystemExit(f"Edge references unknown to node: {edge.get('to')}")


def verify_embedded_json(html_text: str) -> None:
    match = re.search(
        r'<script id="graph-data" type="application/json">(.*?)</script>',
        html_text,
        flags=re.S,
    )
    if not match:
        raise SystemExit("Rendered HTML is missing the graph-data script tag")
    try:
        parsed = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Rendered HTML contains invalid embedded JSON: {exc}") from exc
    if not parsed.get("nodes"):
        raise SystemExit("Rendered HTML embedded JSON has no nodes")


def render_html(data: dict[str, Any], locale: str) -> str:
    zh = locale.lower().startswith("zh")
    default_title = "代码库理解" if zh else "CodeAnalyst"
    default_summary = "一张用于理解代码结构、流程和证据的可视化地图。" if zh else "A visual map of the analyzed codebase."
    title = html.escape(str(data.get("title") or default_title))
    summary = html.escape(str(data.get("summary") or default_summary))
    html_text = (
        HTML_TEMPLATE.replace("__LANG__", html.escape(locale))
        .replace("__TITLE__", title)
        .replace("__SUMMARY__", summary)
        .replace("__DATA_JSON__", script_safe_json(data))
    )
    verify_embedded_json(html_text)
    return html_text


def render_site(graph_json: Path | str, out: Path | str = "site", locale: str | None = None) -> Path:
    graph_path = Path(graph_json).expanduser().resolve()
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    validate_graph(data)
    resolved_locale, render_data = build_render_data(data, locale)

    out_dir = Path(out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "data.json").write_text(
        json.dumps(render_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    html_text = render_html(render_data, resolved_locale)
    (out_dir / "index.html").write_text(html_text, encoding="utf-8")
    return out_dir / "index.html"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a static codebase understanding site.")
    parser.add_argument("graph_json", help="Path to understanding_graph.json")
    parser.add_argument("--out", default="site", help="Output directory")
    parser.add_argument("--locale", help="Override UI locale, for example zh-CN or en")
    args = parser.parse_args()

    index_path = render_site(args.graph_json, args.out, args.locale)
    print(f"Wrote {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
