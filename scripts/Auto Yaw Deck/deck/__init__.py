"""Auto Yaw Deck — Python package (server + panel logic).

Created during P8.1: the former flat deck_*.py modules now live in this
package with their prefix removed (deck_paths -> deck.paths, ...).

Importing the package makes every submodule available as an attribute and
re-exports the public symbols so both styles keep working:

    from deck import state            # module
    from deck.state import DEFAULT_STATE
"""

from deck import (  # noqa: F401
    cert,
    flight,
    http,
    installer,
    instance,
    log,
    panel_i18n,
    paths,
    prefs,
    runner,
    state,
    xplane,
)

# Public symbols re-exported for convenience / backward compatibility.
from deck.log import DEBUG_LOGGING, dlog, set_debug  # noqa: F401
from deck.paths import (  # noqa: F401
    CERT_DIR, COMMANDS_FILE, DATA_DIR, PREFS_FILE,
    SCRIPT_DIR, STATE_FILE, STATIC_DIR,
)
from deck.prefs import load_prefs, save_prefs  # noqa: F401
from deck.state import (  # noqa: F401
    DEFAULT_STATE, get_cached_state, get_xplane_state, read_state_file,
    refresh_state, state_cache, state_lock, write_commands,
)
from deck.cert import (  # noqa: F401
    CertHTTPHandler, generate_self_signed_cert, get_all_local_ips,
    get_local_ip, start_cert_download_server,
)
from deck.http import DeckHTTPHandler  # noqa: F401
from deck.flight import _read_last_aircraft, find_last_airport, start_xplane  # noqa: F401
from deck.installer import get_install_status, install_auto_yaw_deck, install_flywithlua  # noqa: F401
from deck.instance import _cleanup_pid_file, _kill_previous_instances  # noqa: F401
from deck.panel_i18n import PANEL_I18N  # noqa: F401
from deck.xplane import (  # noqa: F401
    XPLANE_EXE_NAMES, _save_xplane_path, clear_deep_search_cache,
    find_xplane_exe, is_xplane_running,
)