# My Prompts Vault

A lightweight Flask app for browsing, filtering, and copying your favourite prompts. Drop Markdown files in the `prompts/` folder and the library updates instantly—perfect for writing, learning, brainstorming, and image generation workflows.

## Features

- Light-first UI with optional dark mode and a wide, responsive masonry grid
- Instant clipboard copy for each prompt (raw Markdown)
- Create, edit, and delete prompts directly from the modal workflow
- Filter by tag or free-text search across titles, descriptions, and content
- Markdown-based storage—no database or external services required

## Project layout

```
app.py                # Flask entrypoint
prompts/              # Your prompt markdown files
static/
  css/styles.css      # Theme and layout styles
  images/             # Optional cover art for prompts
  uploads/            # User-uploaded cover images (auto-created)
templates/index.html  # Jinja2 template for the UI
```

## Prompt file format

Each prompt lives in its own `.md` file inside `prompts/`. Front matter metadata is optional, but helps keep things organised.

```markdown
---
title: Learning Path - Practical AI
description: 24-week roadmap balancing theory, projects, and career polish
tags: curriculum, ai, roadmap
image: images/cover.svg   # optional, relative to static/
---
Your prompt text goes here...
```

Supported metadata keys:

- `title` (string) – displayed as the card title. Defaults to the filename.
- `description` (string) – optional short blurb shown under the title.
- `tags` (comma-separated list) – shown as #tags and used for filtering.
- `image` (string) – path relative to `static/`, e.g. `images/my-cover.svg`.

The Markdown body becomes the rendered preview on each card and the text copied to your clipboard.

## Running locally

### 1. Install dependencies

```bash
/Users/sarathavasarala/Desktop/Projects/my_prompts/.venv/bin/python -m pip install -r requirements.txt
```

### 2. Start the dev server

```bash
FLASK_APP=app.py FLASK_ENV=development /Users/sarathavasarala/Desktop/Projects/my_prompts/.venv/bin/python -m flask run
```

Visit <http://127.0.0.1:5000> to browse your prompts.

## Adding new prompts

Use the **New prompt** button in the top-right corner to launch the creation modal, fill in the form, and optionally upload cover art (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`). Prompts are saved into `prompts/` and images land in `static/uploads/` automatically.

Prefer manual edits? You can still drop a new Markdown file into `prompts/`. For example:

```markdown
---
title: Interview Icebreakers
description: A couple of quick conversation starters for teams meeting for the first time
tags: icebreaker, conversation
---
Share a time when you felt surprisingly proud of a small win.
If time is short, ask each person to finish the sentence: "Lately I've been curious about..."
```

Refresh the page and the new card appears instantly. No reloads or redeploys needed.

## Notes & next steps

- Want to sync prompts across devices? Commit the `prompts/` folder to Git or sync it with your favourite cloud storage.
- You can customise styling via `static/css/styles.css` or extend the template with additional filters and views.
