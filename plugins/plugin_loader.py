import importlib.util
import json
from pathlib import Path


PLUGINS_DIR = Path("/home/adem/graywolf/plugins")


def _load_plugin(plugin_dir: Path) -> dict:
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.exists():
        return {"name": plugin_dir.name, "status": "skipped", "reason": "missing_plugin_json"}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = manifest.get("entry", "plugin.py")
    entry_path = plugin_dir / entry
    if not entry_path.exists():
        return {"name": manifest.get("name", plugin_dir.name), "status": "error", "reason": "missing_entry"}

    spec = importlib.util.spec_from_file_location(f"plugins.{plugin_dir.name}.plugin", str(entry_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    run_result = None
    if hasattr(module, "run"):
        run_result = module.run()

    return {
        "name": manifest.get("name", plugin_dir.name),
        "version": manifest.get("version", "0"),
        "status": "loaded",
        "run_result": run_result,
    }


def load_plugins() -> dict:
    results = []
    if not PLUGINS_DIR.exists():
        return {"status": "ok", "plugins": []}

    for child in sorted(PLUGINS_DIR.iterdir()):
        if not child.is_dir() or child.name.startswith("__"):
            continue
        if child.name == "__pycache__":
            continue
        results.append(_load_plugin(child))

    return {"status": "ok", "plugins": results}


if __name__ == "__main__":
    print(json.dumps(load_plugins(), ensure_ascii=False))
