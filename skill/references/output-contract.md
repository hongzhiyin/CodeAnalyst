# Output Contract

Use this contract when the user wants files, diagrams, or a visual page.

## Output Location

Default persistent artifacts to the central analysis library:

```text
/Users/chihoyo/Project/CodeAnalyst/
  index.md
  analyses/
    <YYYY-MM-DD>-<project-slug>/
      source.md
      overview.md
      architecture.md
      flows.md
      diagrams.md
      open-questions.md
      inventory.json
      flow_map.json
      script_check.json
      import_graph.json
      vibe_audit.json
      understanding_graph.json
      review.md
      review_pack.json
      site_verification.json
      site/
        index.html
        data.json
```

`<YYYY-MM-DD>-<project-slug>` is a naming template, not a literal directory name. Replace it with the actual local date and a slug derived from the target project, such as `2026-06-07-some-app`. Do not include the angle brackets in the real path.

Use a different location only when the user explicitly asks for it.

For long-term maintained projects, the user may ask to use:

```text
TARGET/docs/understanding/
```

Only use the target-project location after the user explicitly chooses it. If the central library cannot be created or written, keep drafts in chat or temporary files and report the blocker.

## Language

Generated artifacts should follow the user's language. For a Chinese request, write Markdown prose, graph labels, flow summaries, evidence details, questions, and visual-site UI labels in Chinese. Keep code identifiers, paths, package names, commands, and established product names unchanged.

## Directory Layout

Create this under the selected output root:

```text
OUTPUT_ROOT/
  source.md
  overview.md
  architecture.md
  flows.md
  diagrams.md
  open-questions.md
  inventory.json
  flow_map.json
  script_check.json
  import_graph.json
  vibe_audit.json
  understanding_graph.json
  review.md
  review_pack.json
  site_verification.json
  site/
    index.html
    data.json
```

For a very small project, combine `architecture.md`, `flows.md`, and `diagrams.md` into `overview.md`.

## Markdown Files

`source.md`:

- Absolute path of the analyzed target
- Analysis date
- Output mode: quick read, understanding pack, or visual pack
- Whether artifacts were written to the central library or the target project

`overview.md`:

- What this project is
- What the user can do with it
- The shortest useful mental model
- Key entrypoints and files
- How to run or inspect it, if known

`architecture.md`:

- Module responsibilities
- Dependency direction
- State and data ownership
- External APIs, files, databases, or tools
- Confirmed facts vs inferences

`flows.md`:

- One section per core user or system flow
- Each section should include trigger, path, side effects, output, and evidence

`diagrams.md`:

- Mermaid diagrams with short captions
- Prefer several readable diagrams over one large graph

`open-questions.md`:

- Unknowns that need runtime inspection, user confirmation, external docs, or missing dependencies
- Suspected dead code or incomplete features

## Evidence Style

Use short evidence notes:

```markdown
Evidence:
- `src/main.tsx` mounts `App`.
- `src/App.tsx` owns the selected-project state.
- Inference: `src/mockData.ts` appears to replace a backend during prototyping.
```

Use absolute file links in final chat responses when possible.

## understanding_graph.json Schema

The visual site renderer accepts this JSON shape:

```json
{
  "title": "Project Name",
  "summary": "One sentence mental model.",
  "locale": "zh-CN",
  "labels": {
    "filterModules": "筛选模块",
    "moduleMap": "模块关系图",
    "selectedModule": "当前模块",
    "coreFlows": "核心流程",
    "evidence": "证据",
    "openQuestions": "开放问题",
    "kindLabels": {
      "entrypoint": "入口",
      "module": "模块",
      "script": "脚本",
      "external": "外部"
    }
  },
  "nodes": [
    {
      "id": "app",
      "label": "App",
      "kind": "component",
      "group": "User interface",
      "layer": "Frontend",
      "path": "src/App.tsx",
      "summary": "Coordinates the main UI."
    }
  ],
  "edges": [
    {
      "from": "app",
      "to": "data",
      "label": "reads",
      "kind": "reads"
    }
  ],
  "flows": [
    {
      "name": "Create item",
      "summary": "How a new item moves from UI input to stored state.",
      "steps": [
        {
          "label": "Submit form",
          "node": "app",
          "path": "src/App.tsx",
          "summary": "The form handler validates input."
        }
      ]
    }
  ],
  "evidence": [
    {
      "claim": "The app is frontend-only.",
      "path": "package.json",
      "detail": "No backend server dependency or API route was found."
    }
  ],
  "questions": [
    "Is mock data intended to be replaced by a real API?"
  ]
}
```

Rules:

- `nodes[].id` must be unique.
- `edges[].from` and `edges[].to` must match node IDs.
- `locale` is optional. If omitted, the renderer infers Chinese UI when graph text contains Chinese; otherwise it defaults to English.
- `labels` is optional. Use it when the user needs localized or domain-specific site UI.
- `nodes[].group` or `nodes[].layer` is optional but recommended. The renderer uses it to create visual lanes so the graph is easier to scan.
- `edges[].kind` is optional but recommended. Use stable verbs such as `imports`, `calls`, `dispatches`, `reads`, `writes`, `renders`, `uses_external_tool`, `fallback_to`, or `syncs_to`.
- Keep summaries short. The site is for navigation, not full documentation.
- Use paths relative to the analyzed project root in JSON; use absolute paths in final chat when citing local files.

## Static Site Expectations

The site should help the user browse:

- module map
- selected node details
- key flows
- evidence and open questions

Do not depend on CDNs, package installs, or a dev server. A single generated `index.html` plus `data.json` is enough.

The site should be visually informative, not only text-heavy:

- group nodes into lanes or layers when possible
- color nodes by role or kind
- label edges with verbs
- render flow steps as an ordered path or timeline
- keep evidence and open questions visible as supporting context

Before delivery, verify:

- `python3 -m json.tool OUTPUT_ROOT/understanding_graph.json`
- `python3 -m json.tool OUTPUT_ROOT/site/data.json`
- `code-analyst verify-site OUTPUT_ROOT/site --out OUTPUT_ROOT/site_verification.json`
- the embedded JSON in `OUTPUT_ROOT/site/index.html` parses; the renderer and `verify-site` both check this
