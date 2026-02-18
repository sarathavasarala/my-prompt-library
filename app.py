import os
import re
import secrets
from functools import wraps
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markdown import markdown as render_markdown
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

app = Flask(__name__)

# --- Auth config -----------------------------------------------------------
# Set these as environment variables (never hard-code them).
# SECRET_KEY: any long random string — used to sign the session cookie.
# APP_PASSWORD: the password you'll enter on first visit.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")

# Session cookie lasts 30 days; HttpOnly + SameSite for basic security.
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,  # 30 days in seconds
)
# ---------------------------------------------------------------------------

PROMPTS_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(f):
    """Redirect to /login if the user has not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        entered = request.form.get("password", "")
        if APP_PASSWORD and secrets.compare_digest(entered, APP_PASSWORD):
            session.permanent = True
            session["authenticated"] = True
            next_url = request.form.get("next") or url_for("index")
            return redirect(next_url)
        error = "Incorrect password. Try again."

    next_url = request.args.get("next", "")
    return render_template("login.html", error=error, next=next_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Template globals
# ---------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    try:
        prompts_dir = PROMPTS_DIR.relative_to(BASE_DIR)
    except ValueError:
        prompts_dir = PROMPTS_DIR
    return {"prompts_dir": prompts_dir}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(value: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    sanitized = re.sub(r"-{2,}", "-", sanitized).strip("-")
    return sanitized or "prompt"


def allowed_image(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def summarize_markdown(text: str, fallback: str = "") -> str:
    if not text:
        return fallback

    cleaned = re.sub(r"`([^`]+)`", r"\1", text)
    cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cleaned)
    cleaned = re.sub(r"[#*>\\-]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) <= 160:
        return cleaned or fallback

    return cleaned[:157].rstrip() + "…"


def delete_uploaded_asset(image_rel_path: str | None) -> None:
    if not image_rel_path:
        return

    if not image_rel_path.startswith("uploads/"):
        return

    asset_path = UPLOAD_DIR / Path(image_rel_path).name
    if asset_path.exists():
        asset_path.unlink()


def parse_prompt_file(path: Path) -> Dict:
    """Parse a markdown prompt file with optional front matter metadata."""
    metadata: Dict[str, str] = {}
    body_lines: List[str] = []

    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    if lines and lines[0].strip() == "---":
        idx = 1
        while idx < len(lines) and lines[idx].strip() != "---":
            line = lines[idx].strip()
            if line and ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()
            idx += 1
        body_lines = lines[idx + 1 :] if idx + 1 < len(lines) else []
    else:
        body_lines = lines

    tags_value = metadata.get("tags", "")
    tags = [tag.strip() for tag in tags_value.split(",") if tag.strip()]

    prompt_text = "".join(body_lines).strip()
    description = metadata.get("description") or summarize_markdown(prompt_text)
    html = render_markdown(
        prompt_text,
        extensions=["extra", "sane_lists", "smarty"],
    )

    return {
        "title": metadata.get("title", path.stem.replace("_", " ").title()),
        "description": description,
        "image": metadata.get("image"),
        "tags": tags,
        "tags_string": tags_value,
        "content": prompt_text,
        "html": html,
        "filename": path.name,
    }


def load_prompts() -> List[Dict]:
    prompt_files = sorted(
        PROMPTS_DIR.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    prompts = [parse_prompt_file(path) for path in prompt_files]
    return [prompt for prompt in prompts if prompt["content"]]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/create")
@login_required
def create_prompt():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    prompt_body = request.form.get("prompt", "").strip()
    tags_input = request.form.get("tags", "").strip()

    if not title or not prompt_body:
        return redirect(url_for("index", error="missing"))

    slug = slugify(title)
    target_path = PROMPTS_DIR / f"{slug}.md"
    counter = 1
    while target_path.exists():
        target_path = PROMPTS_DIR / f"{slug}-{counter}.md"
        counter += 1

    image_rel_path = None
    image = request.files.get("image")
    if image and image.filename:
        if not allowed_image(image.filename):
            return redirect(url_for("index", error="image"))
        safe_name = secure_filename(image.filename)
        ext = Path(safe_name).suffix.lower()
        image_filename = f"{slug}-{uuid4().hex}{ext}"
        image_path = UPLOAD_DIR / image_filename
        image.save(image_path)
        image_rel_path = f"uploads/{image_filename}"

    front_matter = ["---", f"title: {title}"]
    if description:
        front_matter.append(f"description: {description}")
    if tags_input:
        front_matter.append(f"tags: {tags_input}")
    if image_rel_path:
        front_matter.append(f"image: {image_rel_path}")
    front_matter.append("---")

    content_lines = front_matter + ["", prompt_body.strip(), ""]

    with target_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(content_lines))

    return redirect(url_for("index", created="1"))


@app.post("/update")
@login_required
def update_prompt():
    original_filename = request.form.get("original_filename", "").strip()
    original_path = PROMPTS_DIR / original_filename

    if not original_filename or not original_path.exists():
        return redirect(url_for("index", error="missing"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    prompt_body = request.form.get("prompt", "").strip()
    tags_input = request.form.get("tags", "").strip()
    remove_image = request.form.get("remove_image", "0") == "1"

    if not title or not prompt_body:
        return redirect(url_for("index", error="missing"))

    existing_data = parse_prompt_file(original_path)
    image_rel_path = existing_data.get("image")

    slug = slugify(title)
    target_path = PROMPTS_DIR / f"{slug}.md"
    counter = 1
    while target_path.exists() and target_path != original_path:
        target_path = PROMPTS_DIR / f"{slug}-{counter}.md"
        counter += 1

    if remove_image and image_rel_path:
        delete_uploaded_asset(image_rel_path)
        image_rel_path = None

    image = request.files.get("image")
    if image and image.filename:
        if not allowed_image(image.filename):
            return redirect(url_for("index", error="image"))
        if image_rel_path:
            delete_uploaded_asset(image_rel_path)
        safe_name = secure_filename(image.filename)
        ext = Path(safe_name).suffix.lower()
        image_filename = f"{slug}-{uuid4().hex}{ext}"
        image_path = UPLOAD_DIR / image_filename
        image.save(image_path)
        image_rel_path = f"uploads/{image_filename}"

    front_matter = ["---", f"title: {title}"]
    if description:
        front_matter.append(f"description: {description}")
    if tags_input:
        front_matter.append(f"tags: {tags_input}")
    if image_rel_path:
        front_matter.append(f"image: {image_rel_path}")
    front_matter.append("---")

    content_lines = front_matter + ["", prompt_body.strip(), ""]

    with target_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(content_lines))

    if target_path != original_path:
        original_path.unlink(missing_ok=True)

    return redirect(url_for("index", updated="1"))


@app.post("/delete")
@login_required
def delete_prompt():
    filename = request.form.get("filename", "").strip()
    prompt_path = PROMPTS_DIR / filename

    if not filename or not prompt_path.exists():
        return redirect(url_for("index", error="missing"))

    prompt_data = parse_prompt_file(prompt_path)
    image_rel_path = prompt_data.get("image")

    prompt_path.unlink(missing_ok=True)
    delete_uploaded_asset(image_rel_path)

    return redirect(url_for("index", deleted="1"))


@app.route("/")
@login_required
def index():
    prompts = load_prompts()
    tags = sorted({tag for prompt in prompts for tag in prompt["tags"]})
    created = request.args.get("created") == "1"
    updated = request.args.get("updated") == "1"
    deleted = request.args.get("deleted") == "1"
    error = request.args.get("error")
    return render_template(
        "index.html",
        prompts=prompts,
        tags=tags,
        created=created,
        updated=updated,
        deleted=deleted,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
