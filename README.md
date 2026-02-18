# Prompt Library

A lightweight Flask application for managing and organizing text prompts. Store prompts as Markdown files in the `prompts/` folder and access them through a searchable web interface.

![Application Screenshot](app%20screenshot.jpeg)

## Features

- Web-based interface with light and dark mode support
- One-click clipboard copy for each prompt
- Create, edit, and delete prompts through the UI
- Filter by tags or search across titles, descriptions, and content
- File-based storage with optional cover images
- No database required

## Project Structure

```
app.py                # Flask application
prompts/              # Prompt markdown files  ← add your prompts here
static/
  css/styles.css      # Styles
  images/             # Cover art for prompts
  uploads/            # User-uploaded images (auto-created)
templates/
  index.html          # Main template
  login.html          # Login page
api/index.py          # Vercel WSGI adapter
vercel.json           # Vercel deployment config
```

## Prompt File Format

Each prompt is a `.md` file in the `prompts/` directory. Front matter is optional but recommended.

```markdown
---
title: My Prompt Title
description: One-line summary shown on the card
tags: writing, creative
---
Your prompt text goes here. Supports full **Markdown**.
```

Supported front matter fields:

| Field | Description |
|---|---|
| `title` | Card title (defaults to filename if omitted) |
| `description` | Short summary shown on the card |
| `tags` | Comma-separated list for filtering |
| `image` | Path relative to `static/` (e.g. `images/cover.png`) |

## Adding / Editing Prompts

### Option A — Edit files directly (recommended for the deployed site)

Since the deployed Vercel site has a read-only filesystem, the best workflow is:

1. Create or edit a `.md` file in the `prompts/` folder locally
2. Commit and push:
   ```bash
   git add prompts/
   git commit -m "add: my new prompt"
   git push origin main
   ```
3. Vercel auto-deploys in ~30 seconds — done.

**Quick template** — copy this into a new file, e.g. `prompts/my-new-prompt.md`:

```markdown
---
title: My New Prompt
description: What this prompt does
tags: category, another-tag
---
Write your prompt here.

You can use **bold**, _italic_, `code`, bullet lists, etc.
```

### Option B — Use the web UI (local only)

Run the app locally and use the **New prompt** / edit / delete buttons. Changes write directly to the `prompts/` folder on your machine.

```bash
APP_PASSWORD=yourpass SECRET_KEY=anysecret python app.py
```

Then visit `http://127.0.0.1:5000`. When you're happy with your changes, push to GitHub and Vercel picks them up automatically.

## Setup (local)

```bash
pip install -r requirements.txt
APP_PASSWORD=yourpass SECRET_KEY=anysecret python app.py
```

## Deployment (Vercel)

See the [Vercel dashboard](https://vercel.com) — connect the `sarathavasarala/my-prompt-library` repo and set these environment variables:

| Variable | Value |
|---|---|
| `APP_PASSWORD` | Your chosen password |
| `SECRET_KEY` | A long random string (`python -c "import secrets; print(secrets.token_hex(32))"`) |

## Notes

- Prompts are stored as plain files — easy to version control, diff, and back up
- Customize styles by editing `static/css/styles.css`
- Supported image formats: PNG, JPG, JPEG, GIF, WebP, SVG
