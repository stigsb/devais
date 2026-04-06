"""Preview wrapper: delegates to the cad-skill preview.py."""
import sys
from pathlib import Path

# Add the skill directory to the path so we can import preview
_skill_dir = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "cad-skill"
sys.path.insert(0, str(_skill_dir))

from preview import main  # noqa: E402

if __name__ == "__main__":
    main()
