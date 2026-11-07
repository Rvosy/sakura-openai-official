"""Verify ZIP installation and the real Sakura plugin process in an isolated root."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

import yaml


parser = argparse.ArgumentParser()
parser.add_argument("--sakura", required=True, type=Path)
args = parser.parse_args()
sakura = args.sakura.resolve()
root = Path(__file__).resolve().parents[1]
manifest = yaml.safe_load((root / "plugin.yaml").read_text("utf-8"))
service = manifest["id"]
sys.path.insert(0, str(sakura))

from app.core_host.plugin_application import PluginApplicationHost
from app.plugin_sdk.sakura_tools import ToolRegistry
from app.plugins.dependencies import PluginDependencyRoots
from app.plugins.installer import LocalPluginInstaller
from app.storage.runtime_roots import DistributionPaths, RuntimeRoots


with tempfile.TemporaryDirectory(prefix="sakura-openai-host-") as temporary:
    work = Path(temporary)
    distribution = work / "distribution"
    foundation = distribution / "plugins/builtin/sakura_model_openai_compatible"
    shutil.copytree(sakura / "plugins/builtin/sakura_model_openai_compatible", foundation,
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(sakura / "VERSION", distribution / "VERSION")
    uv_dir = distribution / "python/tools"
    uv_dir.mkdir(parents=True)
    uv_name = "uv.exe" if os.name == "nt" else "uv"
    shutil.copy2(sakura / "runtime" / ("Scripts" if os.name == "nt" else "bin") / uv_name, uv_dir / uv_name)
    roots = RuntimeRoots(distribution, work / "user")
    dependencies = PluginDependencyRoots(roots.user_root, distribution_root=distribution)
    with dependencies.prepare("sakura.model.openai_compatible", foundation) as staging:
        bundled = DistributionPaths(distribution).plugin_dependency_root_for("sakura.model.openai_compatible")
        assert staging.resolve().is_relative_to(work.resolve()) and bundled.resolve().is_relative_to(work.resolve())
        bundled.parent.mkdir(parents=True, exist_ok=True)
        staging.replace(bundled)
    package = root / "dist" / f"Sakura-OpenAI-Official-{manifest['version']}.sakplugin.zip"
    LocalPluginInstaller(roots).install(package, "zip", initial_enabled=True)
    host = PluginApplicationHost(roots, "openai-package-verification", ToolRegistry())
    try:
        host.start()
        assert host.wait_until_loaded(timeout=10)
        settings = next(p for p in host.settings_snapshot()["plugins"] if p["pluginId"] == service)
        assert settings["state"] == "active", settings
        assert any(p["serviceKey"] == service for p in host.model_catalog())
        result = host.settings_action(service, "account", "add", {})
        profile = result["values"]["profiles"][0]
        assert profile["account"]["loggedIn"] is False
        result = host.settings_action(service, "account", "remove", {"operationRequest": {"profileId": profile["profileId"]}})
        assert result["values"]["profiles"] == []
        host.set_enabled(settings["installId"], False)
        assert all(p["serviceKey"] != service for p in host.model_catalog())
        print(json.dumps({"installed": service, "version": manifest["version"], "settings": "passed", "cleanup": "passed"}))
    finally:
        host.close()
