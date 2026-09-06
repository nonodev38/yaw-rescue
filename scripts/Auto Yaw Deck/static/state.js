/**
 * AUTO-YAW DECK — State
 * Live state cache, polling loop and the local-change guard that prevents
 * polled values from snapping back while a command is still in flight.
 */

const RECONNECT_INTERVAL = 2000; // ms between reconnect attempts

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let currentState = {};
let isConnected = false;
let pollTimer = null;
let commandTimers = {};

// ---------------------------------------------------------------------------
// Local-change guard — ignore polled state for a key right after we changed
// it ourselves, until the command has had time to reach the Lua bridge.
// ---------------------------------------------------------------------------
const LOCAL_CHANGE_GUARD_MS = 2000;  // 2s guard to prevent slider flicker after command
let recentlyChangedAt = {};

function markRecentlyChanged(key) {
    recentlyChangedAt[key] = Date.now();
}

function isRecentlyChanged(key) {
    const t = recentlyChangedAt[key];
    return t !== undefined && (Date.now() - t) < LOCAL_CHANGE_GUARD_MS;
}

// ---------------------------------------------------------------------------
// Polling
// ---------------------------------------------------------------------------
function startPolling() {
    if (pollTimer) return;
    pollLoop();
}

function pollLoop() {
    fetchState().then(() => {
        pollTimer = setTimeout(pollLoop, POLL_INTERVAL);
    }).catch(() => {
        setConnected(false);
        pollTimer = setTimeout(pollLoop, RECONNECT_INTERVAL);
    });
}

async function fetchState() {
    try {
        const resp = await fetch('/api/state', { cache: 'no-store' });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        currentState = data;
        updateUI(data);
        setConnected(true, data.xplane_active === 'true');
    } catch (e) {
        throw e;
    }
}