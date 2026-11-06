"""Build an installable plugin ZIP without local accounts or test data."""
from pathlib import Path
import zipfile

import yaml


ROOT = Path(__file__).resolve().parents[1]
version = yaml.safe_load((ROOT / "plugin.yaml").read_text("utf-8"))["version"]
output = ROOT / "dist" / f"Sakura-OpenAI-Official-{version}.sakplugin.zip"
output.parent.mkdir(exist_ok=True)
files = [ROOT / name for name in (
    "plugin.yaml", "plugin.py", "profiles.py", "oauth.py", "transport.py",
    "config.json", "requirements.txt", "README.md", "LICENSE", "frontend/account.js",
)]
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, path.relative_to(ROOT).as_posix())
print(output)
