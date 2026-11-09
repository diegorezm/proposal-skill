---
name: proposal
description: Turn a plan into a one-page visual proposal (a self-contained HTML page) that a human can review in a minute — summary, the decisions you need from them with options and your recommendation, the plan as steps, diagrams, risks — and answer inside the page, then paste the answers back. Use when the user runs /proposal, asks for a proposal, a plan to review or "what do you suggest?", or before a large or risky change where you need several decisions from them.
argument-hint: "[what to propose]"
---

# /proposal

Write a short proposal as **data**, render it with the bundled template, show it to the human, and act on the answers they paste back. The page does the design; you do the thinking. Never hand-write the HTML.

Files next to this one: `template.html` (the page), `render.py` (fills the page), `example.json` (a complete example; read it once if you're unsure about a field).

## 1. Think first, then write little

Investigate before you propose: read the code, docs or data the proposal is about. A proposal built on guesses wastes the human's review.

Then decide what the human actually has to judge:
- **Decisions**: real forks where their preference matters. 0–4 of them. Each has 2–4 concrete options, and you mark the one you recommend and say why in one sentence. Never ask about things you can decide yourself or that have a conventional answer.
- **Plan**: 3–8 steps in order, each a title they can approve, change or remove.
- **Diagrams**: only when a picture is faster than text. A `flow` for how parts connect (what's new / changed / removed), a `compare` for before → after. At most 2–3.

Writing rules (the page is read fast, often on a phone):
- Every text field is one or two short sentences. No paragraphs, no markdown, no headings inside fields.
- Plain words. Name things the way the human does, not by internal identifiers (file paths go in `files`).
- Numbers in `facts` must be real (counted, measured or clearly estimated with "~"). Leave `facts` out rather than invent.
- Write in the user's language and set `lang` (`"en"` or `"pt-BR"`; other values fall back to English labels).

## 2. The data

One JSON object. Only `title` is required; everything else is optional and hidden when missing.

| Field | Type | What it is |
| ----- | ---- | ---------- |
| `title` | string | The proposal as an action: "Move sign-in to OAuth". Also the page and file name. |
| `summary` | string | One sentence: what changes and the main effect. |
| `project`, `author`, `date` | string | Shown under the title. `date` defaults to today (`YYYY-MM-DD`). |
| `status` | string | Overrides "Awaiting your decision" in the header. |
| `lang` | string | `"en"` or `"pt-BR"` for the page's own labels. |
| `accent` | string | `"#rrggbb"`; defaults to blue. Use the project's brand color if it has one. |
| `facts` | list of `{value, label}` | 2–4 headline numbers: "9 files changed", "~1 day". |
| `tldr` | `{what, why, ask}` | Three short sentences: what you'll do, why, what you need from them. |
| `decisions` | list | See below. |
| `plan` | list of `{title, detail, effort, risk, files}` | `effort`: `S`/`M`/`L`; `risk`: `low`/`medium`/`high`; `files`: paths touched. |
| `diagrams` | list | See below. |
| `risks` | list of `{level, text, mitigation}` | `level`: `low`/`medium`/`high`. |
| `outOfScope` | list of strings | What this proposal deliberately doesn't do. |
| `questions` | list of strings | Things you couldn't find out and they might know. |
| `links` | list of `{label, url}` | Issues, docs, dashboards, PRs. |
| `id` | string | Optional stable id; answers are remembered per id in the viewer's browser. |

**Decision**: `{ id, question, context, multi, options: [{ id, label, detail, pros, cons, recommended }], why }`
- `multi: true` lets them pick several options (checkboxes); otherwise one.
- Mark `recommended: true` on your pick(s) and put the reason in `why`.
- Give every option an `id` (short, unique within the decision).

**Diagram, flow**: `{ type: "flow", title, caption, nodes: [{ id, label, note, tone }], edges: [[from, to, label?]] }`
- `tone`: `new`, `changed`, `removed` or leave it out (unchanged). The legend appears by itself.
- Nodes are laid out left → right by dependency. Keep labels under ~20 characters and notes under ~26; 3–7 nodes read best.

**Diagram, compare**: `{ type: "compare", title, caption, before: [...], after: [...], beforeLabel, afterLabel }`
- Items are strings or `{ text, tone }` with the same tones.

## 3. Render

Write the JSON to a temporary file, then run the renderer from this skill's folder:

```sh
python3 <skill folder>/render.py proposal.json --open     # writes .claude/proposals/<date>-<slug>.html
python3 <skill folder>/render.py proposal.json out.html   # or choose the path
```

Use `python` instead of `python3` where that's the command. It prints the output path, and it refuses invalid data with a list of problems; fix them and run it again. If Python isn't available, copy `template.html` and replace `/*PROPOSAL_TITLE*/` with the HTML-escaped title and `/*PROPOSAL_DATA*/` with the JSON (with every `</` written as `<\/`).

Run it from the user's project folder: by default it saves to `.claude/proposals/` at the project root (or `~/.claude/proposals/` outside a project). If the project is a git repository and `.claude/proposals/` isn't ignored, mention once that they may want to add it to `.gitignore`; don't edit `.gitignore` yourself unless they ask.

## 4. Show it

Open it in the browser with `--open` and give the file path. Don't publish it anywhere (no Artifact, no upload, no preview tool) unless the user explicitly asks for that.

Then write a short chat message: one line on what you're proposing, the decisions you need (numbered, with your recommendation), and that they can answer in the page and paste the copied answers back — or just reply in chat. Don't repeat the whole proposal in the chat.

## 5. Act on the answers

The page's **Copy my answers** button produces Markdown like:

```
## Answers to the proposal: Move sign-in to OAuth

### Decisions
1. Which providers should we offer? → **Google**, **GitHub**
2. What if an OAuth email doesn't match any account? → **Ask them to link manually** (not the recommendation)
   > we had duplicate-account complaints last year

### Plan
- Step 4 "Remove passwords": **Change** — keep passwords for admins
- Approved steps: 1, 2, 3, 5

### General note
Start after the release on Friday.
```

When it arrives:
- Treat each choice as decided. Where they went against your recommendation, follow them; mention a real risk once if there is one, then don't relitigate.
- "Change" steps: apply their note. "Remove" steps: drop them. Steps with no answer: assume approved unless that would be risky; then ask about just those.
- If the answers change the plan a lot, update the JSON, render it again (same `id`), and show the new version; otherwise start the work.
- Answers in plain chat are just as valid as the pasted block.

## When not to use it

A single yes/no question, a tiny change, or something the user asked you to just do: ask in chat or do it. The page is for proposals with several moving parts.
