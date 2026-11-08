# /proposal

A Claude Code skill that turns an AI's plan into a **one-page visual proposal** you can review in a
minute and answer right on the page.

Long plans in a chat are hard to review: the decisions hide in paragraphs, and replying means
re-typing context. `/proposal` puts it on one page instead:

- **In short**: what the AI will do, why, and what it needs from you.
- **Decisions**: each fork with 2–4 options, pros and cons, and the AI's recommendation with a reason.
  You click your choice and add a note.
- **Plan**: the steps in order, with effort, risk and the files they touch. Approve, change or remove each one.
- **Diagrams**: how the parts connect (new, changed and removed parts marked) and before → after views.
- **Risks**, out of scope, open questions and links.
- **Copy my answers**: one button turns your choices into a short Markdown reply to paste back in the chat.

![A proposal page](docs/light.png)

It also has a dark theme, works on phones, and never touches the network: the page is one self-contained
HTML file with no libraries, fonts or trackers.

## Install

**As a plugin** (Claude Code):

```
/plugin marketplace add diegorezm/proposal-skill
/plugin install proposal@proposal-skill
```

**By hand**: copy `skills/proposal/` into `~/.claude/skills/` (all your projects) or into
`.claude/skills/` inside one project.

The renderer needs Python 3.8+ (standard library only). Without Python, the skill tells the AI how to
fill the template by hand.

## Use

```
/proposal move our sign-in to OAuth
```

Or just ask for a proposal or a plan to review; the skill also kicks in before big changes where the
AI needs several decisions from you. The AI investigates, writes the proposal as data, renders the page
and opens it (or publishes it, if your client has a page/Artifact tool). Answer in the page, click
**Copy my answers**, paste into the chat, and the AI continues from your choices.

See a full example: [`examples/oauth.html`](examples/oauth.html) (open it in a browser) and the data
behind it, [`skills/proposal/example.json`](skills/proposal/example.json).

## How it works

```
skills/proposal/
├── SKILL.md        instructions for the AI: when to propose, how to write it, the data format
├── template.html   the page: layout, themes, diagrams and the answer logic, drawn from JSON
├── render.py       checks the JSON and writes one HTML file (temp folder by default)
└── example.json    a complete proposal using every field
```

The AI never writes HTML. It writes a small JSON object (title, summary, decisions, plan, diagrams,
risks…) and `render.py` injects it into the template, so every proposal looks the same and renders
correctly. Answers are remembered in your browser until you click **Clear**.

Render one yourself:

```sh
python skills/proposal/render.py skills/proposal/example.json out.html --open
```

### Customizing

- `accent` in the JSON sets the color (`"#rrggbb"`), e.g. your project's brand color.
- `lang` switches the page's own labels: `en` and `pt-BR` are built in. To add a language, add an entry
  to `LABELS` in `template.html`.
- Diagrams: `flow` (boxes and arrows, laid out automatically) and `compare` (before → after).

## License

MIT
