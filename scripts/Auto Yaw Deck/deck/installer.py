"""FlyWithLua + Auto Yaw Deck installer (étape P2.2).

Downloads FlyWithLua NXT into X-Plane's Resources/plugins and installs the
Auto Yaw Deck Lua scripts into the plugin's Scripts folder.
"""
import shutil
from pathlib import Path

FLYWITHLUA_URL = "https://github.com/X-FriX/FlyWithLua/releases/download/latest/FlyWithLua_NXT.zip"


def _find_flywithlua_dir(xplane_root):
    """Find the FlyWithLua plugin directory in X-Plane."""
    if not xplane_root:
        return None
    root = Path(xplane_root)
    plugins_dir = root / "Resources" / "plugins"
    if not plugins_dir.is_dir():
        return None
    for d in plugins_dir.iterdir():
        if d.is_dir():
            name_lower = d.name.lower()
            if "flywithlua" in name_lower or "fly_with_lua" in name_lower:
                return d
    return None


def _is_flywithlua_installed(xplane_root):
    """Check if FlyWithLua is installed."""
    fl_dir = _find_flywithlua_dir(xplane_root)
    return (True, fl_dir) if fl_dir else (False, None)


def _get_scripts_dir(xplane_root):
    """Get the Scripts directory inside FlyWithLua. Creates it if missing."""
    fl_dir = _find_flywithlua_dir(xplane_root)
    if not fl_dir:
        return None
    scripts = fl_dir / "Scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    return scripts


def install_flywithlua(xplane_root):
    """Download and install FlyWithLua NXT into X-Plane."""
    import urllib.request
    import zipfile
    import tempfile

    root = Path(xplane_root)
    plugins_dir = root / "Resources" / "plugins"
    if not plugins_dir.is_dir():
        return False, "Plugins directory not found"
    try:
        tmp_dir = Path(tempfile.mkdtemp())
        zip_path = tmp_dir / "FlyWithLua_NXT.zip"
        urllib.request.urlretrieve(FLYWITHLUA_URL, str(zip_path))
        with zipfile.ZipFile(str(zip_path), 'r') as zf:
            zf.extractall(str(plugins_dir))
        zip_path.unlink(missing_ok=True)
        tmp_dir.rmdir(ignore_errors=True)
        return True, "FlyWithLua NXT installed successfully"
    except Exception as e:
        return False, f"Installation failed: {e}"


def install_auto_yaw_deck(xplane_root):
    """Install Auto Yaw Deck files into FlyWithLua/Scripts.

    IMPORTANT: If the script is already running from the destination directory,
    we skip the folder copy to avoid deleting ourselves. Only the Lua files
    are copied/updated in that case.
    """
    root = Path(xplane_root)
    scripts_dir = _get_scripts_dir(xplane_root)
    if not scripts_dir:
        return False, "FlyWithLua Scripts directory not found"

    src_dir = Path(__file__).resolve().parent
    running_in_place = (src_dir == scripts_dir / "Auto Yaw Deck")

    try:
        # 1. Copy Auto Yaw Deck folder (skip if running from destination)
        dst_deck = scripts_dir / "Auto Yaw Deck"
        if not running_in_place:
            if dst_deck.exists():
                shutil.rmtree(str(dst_deck))
            shutil.copytree(str(src_dir), str(dst_deck))

        # 2. Copy auto_yaw_deck.lua to Scripts/
        src_bridge = src_dir / ".." / ".." / "auto_yaw_deck.lua"
        if not src_bridge.is_file():
            src_bridge = src_dir.parent / "auto_yaw_deck.lua"
        if src_bridge.is_file():
            shutil.copy2(str(src_bridge), str(scripts_dir / "auto_yaw_deck.lua"))

        # 3. Copy auto_yaw.lua to Scripts/
        src_yaw = src_dir.parent / "auto_yaw.lua"
        if src_yaw.is_file():
            shutil.copy2(str(src_yaw), str(scripts_dir / "auto_yaw.lua"))

        # 4. Cleanup: remove certs directory from installed copy
        if dst_deck.exists():
            dst_certs = dst_deck / "certs"
            if dst_certs.exists():
                shutil.rmtree(str(dst_certs))

        # 5. Cleanup: remove AutoYaw_profiles.cfg backup if present
        for cfg_name in ["AutoYaw_profiles.cfg", "AutoYaw_profiles.cfg.bak"]:
            cfg_file = scripts_dir / cfg_name
            if cfg_file.is_file():
                cfg_file.unlink()
        dst_cfg = dst_deck / "AutoYaw_profiles.cfg"
        if dst_cfg.is_file():
            dst_cfg.unlink()

        return True, f"Auto Yaw Deck installed to {scripts_dir}"
    except Exception as e:
        return False, f"Installation failed: {e}"


def get_install_status(xplane_root):
    """Check the installation status of FlyWithLua and Auto Yaw Deck."""
    status = {
        "flywithlua": False, "flywithlua_dir": None,
        "auto_yaw_deck": False, "auto_yaw_lua": False, "auto_yaw_deck_lua": False,
    }
    fl_installed, fl_dir = _is_flywithlua_installed(xplane_root)
    status["flywithlua"] = fl_installed
    status["flywithlua_dir"] = str(fl_dir) if fl_dir else None
    if fl_dir:
        scripts = fl_dir / "Scripts"
        status["auto_yaw_deck"] = (scripts / "Auto Yaw Deck").is_dir()
        status["auto_yaw_lua"] = (scripts / "auto_yaw.lua").is_file()
        status["auto_yaw_deck_lua"] = (scripts / "auto_yaw_deck.lua").is_file()
    return status
