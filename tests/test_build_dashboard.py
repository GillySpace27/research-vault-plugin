import sys, unittest, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_dashboard as bd


def _vault(root: Path):
    (root / "projects").mkdir()
    (root / "proposals").mkdir()
    (root / "memory" / "people").mkdir(parents=True)
    (root / "daily_notes").mkdir()
    (root / "_templates").mkdir()
    (root / "projects" / "alpha.md").write_text("# Alpha\n- [ ] do alpha thing\n", encoding="utf-8")
    (root / "proposals" / "calls.md").write_text("# Calls\n- [ ] watch NSF call\n", encoding="utf-8")
    (root / "inbox.md").write_text("# Inbox\n- [ ] loose task\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("# mem\n- [ ] should be skipped\n", encoding="utf-8")
    (root / "memory" / "people" / "p.md").write_text("# P\n- [ ] not a task file\n", encoding="utf-8")
    (root / "daily_notes" / "2026-01-01.md").write_text("# day\n- [ ] journal item\n", encoding="utf-8")
    (root / "_templates" / "project.md").write_text("# tmpl\n- [ ] placeholder\n", encoding="utf-8")


class TestWalkVault(unittest.TestCase):
    def test_recurses_and_skips(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _vault(root)
            keys = set(bd.walk_vault(root).keys())
            self.assertEqual(keys, {"projects/alpha.md", "proposals/calls.md", "inbox.md"})

    def test_keys_are_sorted_folder_first(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _vault(root)
            keys = list(bd.walk_vault(root).keys())
            self.assertEqual(keys, sorted(keys))

    def test_flat_vault_still_works(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "rhef.md").write_text("# RHEF\n- [ ] flat task\n", encoding="utf-8")
            (root / "README.md").write_text("# r\n- [ ] skip me\n", encoding="utf-8")
            self.assertEqual(set(bd.walk_vault(root).keys()), {"rhef.md"})


if __name__ == "__main__":
    unittest.main()
