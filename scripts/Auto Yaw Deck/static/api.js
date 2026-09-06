/**
 * AUTO-YAW DECK — API client
 * Sends commands to the Python server (written to data/commands.txt and
 * applied by the Lua bridge).
 */

function sendCommand(key, value) {
    const body = JSON.stringify({ [key]: value });
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body
    }).catch(e => console.warn('Command failed:', e));
}

function sendCommands(commands) {
    const body = JSON.stringify({ commands });
    fetch('/api/commands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body
    }).catch(e => console.warn('Commands failed:', e));
}