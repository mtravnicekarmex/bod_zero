from __future__ import annotations

import subprocess
from pathlib import Path


def commit_and_push(project_root: Path, message: str) -> bool:
    """Stages everything, commits with `message`, and pushes.

    Returns True if a commit was made, False if there was nothing to
    commit (not an error — the pipeline may call this at a point where the
    working tree is already clean). Raises RuntimeError on any git failure
    (including a failed push), so the caller sees it and does not proceed
    on top of an unsaved state (see PRINCIPLES.md P3).
    """
    _run_git(project_root, ["add", "-A"])

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=project_root,
    )
    if diff.returncode == 0:
        return False

    _run_git(project_root, ["commit", "-m", message])
    _refuse_template_origin(project_root)
    _run_git(project_root, ["push"])
    return True


def _refuse_template_origin(project_root: Path) -> None:
    """Blocks the push if `origin` still points at a point-zero template.

    Structural guard, not just a documented step (see PRINCIPLES.md P4) —
    this is the exact mistake that landed real project work on the
    `bod-nula` template repo instead of a dedicated project repo. Silently
    does nothing if `TEMPLATE_ORIGINS.md` or a git remote named `origin`
    is missing, so unrelated setups (including the test suite) are
    unaffected.
    """
    template_file = project_root / "TEMPLATE_ORIGINS.md"
    if not template_file.exists():
        return

    origin = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if origin.returncode != 0:
        return

    templates = {
        _normalize_remote(line)
        for line in template_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    if _normalize_remote(origin.stdout) in templates:
        raise RuntimeError(
            f"Refusing to push: origin ({origin.stdout.strip()}) is still a "
            "point-zero template repository listed in TEMPLATE_ORIGINS.md. "
            "Create a new, dedicated repository for this project and run "
            "`git remote set-url origin <new-repo-url>` before continuing."
        )


def _normalize_remote(url: str) -> str:
    url = url.strip().lower()
    if url.endswith(".git"):
        url = url[: -len(".git")]
    return url.rstrip("/")


def _run_git(project_root: Path, args: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result
