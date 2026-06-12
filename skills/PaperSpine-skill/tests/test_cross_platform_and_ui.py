from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUITE_SKILLS = [
    "paper-spine",
    "paper-spine-ui",
    "paper-spine-intake",
    "paper-spine-research",
    "paper-spine-citation",
    "paper-spine-rewrite",
    "paper-spine-build",
    "paper-spine-latex",
    "paper-spine-audit",
    "paper-spine-translate",
    "paper-spine-humanize",
    "paper-spine-update",
]

WORKER_SKILLS = [
    "paper-spine-ui",
    "paper-spine-intake",
    "paper-spine-research",
    "paper-spine-citation",
    "paper-spine-rewrite",
    "paper-spine-build",
    "paper-spine-latex",
    "paper-spine-audit",
    "paper-spine-translate",
    "paper-spine-humanize",
]


def all_skill_docs() -> list[Path]:
    docs = list((ROOT / "dist").rglob("SKILL.md"))
    docs += list((ROOT / "dist").rglob("interactive-intake.md"))
    return docs


def frontmatter_value(skill_md: Path, field: str) -> str:
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"{skill_md}: missing frontmatter '{field}'")


class CodexSingleEntryTests(unittest.TestCase):
    """Guarantee #1: Codex sees exactly one 'paper-spine', plus the full suite."""

    def test_codex_install_exposes_single_paper_spine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable, "src/scripts/sync_local_installs.py", "--clean-legacy",
                    "--desktop-root", str(base / "desktop"),
                    "--codex-skills-dir", str(base / "codex" / "skills"),
                    "--claude-skills-dir", str(base / "claude" / "skills"),
                    "--claude-commands-dir", str(base / "claude" / "commands"),
                    "--openclaw-skills-dir", str(base / "openclaw" / "skills"),
                    "--codex-prompts-dir", str(base / "codex" / "prompts"),
                    "--config-home", str(base / "config"),
                ],
                cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            # The /paperspine slash command must install for Codex too.
            self.assertTrue((base / "codex" / "prompts" / "paperspine.md").exists())
            codex = base / "codex" / "skills"

            ps_dirs = [p for p in codex.iterdir() if p.is_dir() and p.name == "paper-spine"]
            self.assertEqual(len(ps_dirs), 1, "expected exactly one paper-spine directory")

            names = [
                frontmatter_value(d / "SKILL.md", "name")
                for d in codex.iterdir() if (d / "SKILL.md").exists()
            ]
            self.assertEqual(names.count("paper-spine"), 1, f"duplicate paper-spine name: {names}")
            self.assertEqual(len(names), len(set(names)), f"non-unique skill names: {names}")

            for skill in SUITE_SKILLS:
                self.assertTrue((codex / skill / "SKILL.md").exists(), f"missing {skill}")
            for legacy in ("PaperSpine", "PaperSpineV2"):
                self.assertFalse((codex / legacy).exists(), f"legacy {legacy} should not install")


class UiAutoLaunchTests(unittest.TestCase):
    """Guarantee #1b: the UI launches by ABSOLUTE installed path, automatically."""

    def test_no_relative_launcher_invocation_in_docs(self) -> None:
        bad: list[str] = []
        for doc in all_skill_docs():
            text = doc.read_text(encoding="utf-8")
            if "-File scripts/launch_paperspine_ui.ps1" in text or "python scripts/intake_wizard.py" in text:
                bad.append(str(doc.relative_to(ROOT)))
        self.assertEqual(bad, [], "docs must invoke the launcher by absolute install path")

    def test_launcher_referenced_by_absolute_install_path(self) -> None:
        ui = (ROOT / "dist" / "claude" / "skills" / "paper-spine-ui" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(r"$env:USERPROFILE\.codex\skills\paper-spine-ui\scripts\launch_paperspine_ui.ps1", ui)
        self.assertIn(r"$env:USERPROFILE\.claude\skills\paper-spine-ui\scripts\launch_paperspine_ui.ps1", ui)

    def test_codex_paperspine_slash_command_exists_and_routes_to_orchestrator(self) -> None:
        prompt = ROOT / "dist" / "codex" / "prompts" / "paperspine.md"
        self.assertTrue(prompt.exists(), "Codex /paperspine custom prompt must ship")
        text = prompt.read_text(encoding="utf-8")
        self.assertIn("$paper-spine", text)  # routes to the orchestrator skill
        self.assertIn("description:", text)  # valid custom-prompt frontmatter
        self.assertNotIn("-File scripts/launch_paperspine_ui.ps1", text)  # absolute path only
        self.assertIn(r"$env:USERPROFILE\.codex\skills", text)
        # Hard execution constraint: launch UI first, with escalation.
        self.assertIn("require_escalated", text)
        self.assertIn("FIRST tool action", text)

    def test_orchestrator_auto_launches_ui_when_config_missing(self) -> None:
        orch = (ROOT / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md").read_text(encoding="utf-8").lower()
        for token in ("configuration is missing", "launch", "intake", "automatically"):
            self.assertIn(token, orch, f"orchestrator must describe auto-launch ({token})")
        # Codex hard constraint: launch UI as the first action, with escalation.
        self.assertIn("require_escalated", orch)
        self.assertIn("first tool", orch)


class CrossPlatformLauncherTests(unittest.TestCase):
    """Guarantee #2: Windows, macOS, and Linux are all supported."""

    def test_ui_launchers_exist_for_all_platforms(self) -> None:
        self.assertTrue((ROOT / "src" / "scripts" / "launch_paperspine_ui.ps1").exists(), "Windows launcher")
        self.assertTrue((ROOT / "src" / "scripts" / "launch_paperspine_ui.sh").exists(), "macOS/Linux launcher")

    def test_shell_launcher_supports_macos_and_linux(self) -> None:
        sh = (ROOT / "src" / "scripts" / "launch_paperspine_ui.sh").read_text(encoding="utf-8")
        self.assertIn("Darwin", sh)
        self.assertIn("osascript", sh)
        self.assertIn("Linux", sh)
        self.assertTrue(
            any(term in sh for term in ("gnome-terminal", "konsole", "xterm")),
            "shell launcher must support at least one Linux terminal emulator",
        )

    def test_powershell_launcher_forces_utf8(self) -> None:
        ps = (ROOT / "src" / "scripts" / "launch_paperspine_ui.ps1").read_text(encoding="utf-8")
        self.assertIn("chcp 65001", ps)
        self.assertIn("UTF8", ps)

    def test_intake_wizard_handles_windows_and_posix(self) -> None:
        wiz = (ROOT / "src" / "scripts" / "intake_wizard.py").read_text(encoding="utf-8")
        self.assertIn("msvcrt", wiz, "Windows key input")
        self.assertIn("termios", wiz, "POSIX key input")
        self.assertIn("tty", wiz, "POSIX raw mode")
        self.assertIn("ENABLE_VIRTUAL_TERMINAL_PROCESSING", wiz, "Windows ANSI enabling")
        self.assertIn("chcp 65001", wiz, "Windows UTF-8 codepage")


class OrchestratorDiscoverabilityTests(unittest.TestCase):
    """The main skill must be intent-discoverable in Codex (no anti-trigger desc)."""

    def test_orchestrator_description_is_trigger_rich(self) -> None:
        desc = frontmatter_value(
            ROOT / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md", "description"
        )
        low = desc.lower()
        # Must read like a task trigger, not an internal note that hides it.
        self.assertNotIn("internal orchestrator", low)
        self.assertNotIn("users should use /paperspine", low)
        self.assertTrue(
            any(verb in low for verb in ("write", "rewrite", "build")),
            "orchestrator description needs an action verb so Codex surfaces it",
        )
        self.assertIn("paper", low)
        self.assertLessEqual(len(desc), 200)

    def test_orchestrator_not_marked_internal_step(self) -> None:
        # The entry point must NOT carry the worker "(internal ... step)" marker.
        desc = frontmatter_value(
            ROOT / "dist" / "claude" / "skills" / "paper-spine" / "SKILL.md", "description"
        )
        self.assertNotIn("internal /paperspine step", desc.lower())


class WorkerVisibilityTests(unittest.TestCase):
    """Guarantee #3: worker skills stay VISIBLE (never auto-hidden)."""

    def test_no_skills_are_marked_internal_for_hiding(self) -> None:
        sys.path.insert(0, str(ROOT / "src" / "scripts"))
        import sync_local_installs  # noqa: PLC0415

        self.assertEqual(
            sync_local_installs.PAPERSPINE_INTERNAL_SKILLS, set(),
            "no PaperSpine skill may be flagged for hiding",
        )

    def test_all_suite_skills_ship_in_every_host(self) -> None:
        for host in ("claude", "codex", "openclaw"):
            for skill in SUITE_SKILLS:
                self.assertTrue(
                    (ROOT / "dist" / host / "skills" / skill / "SKILL.md").exists(),
                    f"{host}:{skill} must be installed and visible",
                )

    def test_worker_descriptions_stay_under_portable_limit(self) -> None:
        for skill in WORKER_SKILLS:
            desc = frontmatter_value(ROOT / "dist" / "claude" / "skills" / skill / "SKILL.md", "description")
            self.assertLessEqual(len(desc), 200, f"{skill} description exceeds 200 chars")


if __name__ == "__main__":
    unittest.main()
