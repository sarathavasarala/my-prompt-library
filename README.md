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
prompts/              # Prompt markdown files
static/
  css/styles.css      # Styles
  images/             # Cover art for prompts
  uploads/            # User-uploaded images (auto-created)
templates/index.html  # Main template
```

## Prompt File Format

Each prompt is stored as a `.md` file in the `prompts/` directory. Front matter metadata is optional but recommended for organization.

```markdown
---
title: Example Prompt
description: A brief description of what this prompt does
tags: example, demo
image: images/cover.svg
---
Your prompt text goes here...
```

Supported metadata:

- `title` – Card title (defaults to filename if not specified)
- `description` – Brief summary shown on the card
- `tags` – Comma-separated list for filtering
- `image` – Path relative to `static/` directory

The Markdown body is rendered as a preview and copied to the clipboard when the copy button is clicked.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

The application will start at `http://127.0.0.1:5000`.

## Usage

### Adding Prompts

Use the **New prompt** button to create prompts through the web interface. You can add a title, description, tags, and upload cover images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`).

Alternatively, create Markdown files directly in the `prompts/` directory:

```markdown
---
title: Example Template
description: Quick description of the prompt
tags: template, example
---
Your prompt content here.
```

Refresh the page to see new prompts appear.

### Editing and Deleting

Click on any prompt card to view, edit, or delete it. Changes are reflected immediately in the file system.

## Notes

- Prompts are stored as files, making them easy to version control with Git or sync with cloud storage
- Customize the interface by editing `static/css/styles.css`
- Supported image formats: PNG, JPG, JPEG, GIF, WebP, SVG
