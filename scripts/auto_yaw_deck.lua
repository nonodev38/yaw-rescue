-- AUTO-YAW DECK — Bridge script
-- Reads X-Plane datarefs and writes state to file for the Python server.
-- Reads commands from file and applies them to X-Plane.
--
-- Place this alongside auto_yaw.lua in Scripts/

logMsg("[AUTO-YAW DECK] Loading bridge script")

-- ---------------------------------------------------------------------------
-- Data directories
-- ---------------------------------------------------------------------------
local deck_dir = SCRIPT_DIRECTORY .. "Auto Yaw Deck/"
local data_dir = deck_dir .. "data/"
local state_file = data_dir .. "state.txt"
local commands_file = data_dir .. "commands.txt"

-- Ensure data directory exists (create via io)
pcall(os.execute, 'mkdir "' .. data_dir:gsub("/", "\\") .. '" 2>nul || mkdir -p "' .. data_dir .. '"')

-- ---------------------------------------------------------------------------
-- Datarefs — matching auto_yaw.lua references
-- ---------------------------------------------------------------------------
local dr_axis = dataref_table("sim/joystick/joy_mapped_axis_value")
local dr_phi = dataref_table("sim/flightmodel/position/phi")
local dr_psi = dataref_table("sim/flightmodel/position/psi")
local dr_alt = dataref_table("sim/flightmodel/position/elevation")
local dr_ias = dataref_table("sim/cockpit2/gauges/indicators/airspeed_kts_pilot")
local dr_heading = dataref_table("sim/flightmodel/position/magpsi")
local dr_aircraft = dataref_table("sim/aircraft/view/acf_descrip")
local dr_vfe = dataref_table("sim/aircraft/view/acf_Vfe")  -- max flap-extended speed (kias)
-- Landing gear + flight vitals (per-engine arrays, gear deploy ratios)
local dr_gear = dataref_table("sim/flightmodel2/gear/deploy_ratio")
local dr_rpm = dataref_table("sim/cockpit2/engine/indicators/engine_speed_rpm")
local dr_thro = dataref_table("sim/flightmodel/engine/ENGN_thro")
local dr_vspd = dataref_table("sim/flightmodel/position/vh_ind_fpm")
local dr_alpha = dataref_table("sim/flightmodel/position/alpha")

-- Writable datarefs for commands
local dr_flap_ratio = dataref_table("sim/cockpit2/controls/flap_ratio", "writable")
-- NOTE: trim is applied as offsets in auto_yaw.lua's process_outputs(),
-- so no trim datarefs needed here.

-- Retract-flaps alert state (hysteresis to avoid flicker)
local flap_alert_on = false

-- ---------------------------------------------------------------------------
-- Config keys shared with auto_yaw.lua's (now global) `config` table
-- ---------------------------------------------------------------------------
local CONFIG_BOOL_KEYS = {
    enabled = true, smoothing_enabled = true, deadzone_enabled = true,
    auto_coord_enabled = true, yaw_damper_enabled = true,
}
local CONFIG_NUM_KEYS = {
    smoothing_factor = true, deadzone_size = true, auto_coord_gain = true,
    coord_bank_limit = true, damper_gain = true, damper_sensitivity = true, noise_filter = true,
}
local CONFIG_STR_KEYS = {
    lang = true,
}

-- ---------------------------------------------------------------------------
-- State writer — writes current X-Plane data to state.txt
-- ---------------------------------------------------------------------------
local function write_state()
    local file = io.open(state_file, "w")
    if not file then return end

    local cfg = config or {}
    local st = state or {}  -- read from auto_yaw.lua's computed state
    local alt = (dr_alt[0] or 0.0) * 3.28084  -- meters to feet
    local ias = dr_ias[0] or 0.0
    local hdg = dr_heading[0] or 0.0

    -- Retract-flaps alert: it's time to raise the flaps when the airspeed
    -- reaches the max flap-extended speed (Vfe) while flaps are still out
    local vfe = dr_vfe[0] or 0.0
    local flap_out = (dr_flap_ratio[0] or 0.0) > 0.02
    if flap_out and vfe > 0 then
        if ias >= vfe then
            flap_alert_on = true
        elseif ias < vfe - 5.0 then
            flap_alert_on = false
        end
    else
        flap_alert_on = false
    end

    -- Landing gear (nose/left/right) + engine & flight vitals
    local gear0 = dr_gear[0] or 0.0
    local gear1 = dr_gear[1] or 0.0
    local gear2 = dr_gear[2] or 0.0
    local rpm = 0.0
    local throttle = 0.0
    for i = 0, 7 do
        local r = dr_rpm[i]
        local t = dr_thro[i]
        if r and r > rpm then rpm = r end
        if t and t > throttle then throttle = t end
    end
    local vspd = dr_vspd[0] or 0.0
    local alpha_deg = dr_alpha[0] or 0.0

    -- Write all state as key=value pairs — reads real computed values from auto_yaw.lua
    file:write("# Auto-Yaw Deck state — do not edit\n")
    file:write(string.format("bank_angle=%.4f\n", st.bank_angle or 0.0))
    file:write(string.format("yaw_rate=%.4f\n", st.yaw_rate or 0.0))
    file:write(string.format("heading=%.2f\n", hdg))
    file:write(string.format("altitude=%.0f\n", alt))
    file:write(string.format("airspeed=%.1f\n", ias))
    file:write(string.format("raw_input=%.4f\n", st.raw_input or 0.0))
    file:write(string.format("smoothed_input=%.4f\n", st.smoothed_input or 0.0))
    file:write(string.format("final_output=%.4f\n", st.final_output or 0.0))
    file:write(string.format("auto_coord_output=%.4f\n", st.auto_coord_output or 0.0))
    file:write(string.format("damper_output=%.4f\n", st.damper_output or 0.0))
    file:write(string.format("elevator_trim=%.4f\n", cfg.elevator_trim or 0.0))
    file:write(string.format("aileron_trim=%.4f\n", cfg.aileron_trim or 0.0))
    file:write(string.format("rudder_trim=%.4f\n", cfg.rudder_trim or 0.0))
    file:write(string.format("flap_ratio=%.4f\n", cfg.flap_ratio or dr_flap_ratio[0] or 0.0))
    file:write(string.format("flap_vfe=%.0f\n", vfe))
    file:write(string.format("flap_alert=%s\n", tostring(flap_alert_on)))
    file:write(string.format("gear_nose=%.2f\n", gear0))
    file:write(string.format("gear_left=%.2f\n", gear1))
    file:write(string.format("gear_right=%.2f\n", gear2))
    file:write(string.format("rpm=%.0f\n", rpm))
    file:write(string.format("throttle=%.2f\n", throttle))
    file:write(string.format("vspd_fpm=%.0f\n", vspd))
    file:write(string.format("alpha_deg=%.1f\n", alpha_deg))
    file:write(string.format("active_aircraft=%s\n", tostring(dr_aircraft[0] or "")))
    file:write(string.format("enabled=%s\n", tostring(cfg.enabled)))
    file:write(string.format("smoothing_enabled=%s\n", tostring(cfg.smoothing_enabled)))
    file:write(string.format("deadzone_enabled=%s\n", tostring(cfg.deadzone_enabled)))
    file:write(string.format("auto_coord_enabled=%s\n", tostring(cfg.auto_coord_enabled)))
    file:write(string.format("yaw_damper_enabled=%s\n", tostring(cfg.yaw_damper_enabled)))
    file:write(string.format("smoothing_factor=%.4f\n", cfg.smoothing_factor or 0.15))
    file:write(string.format("deadzone_size=%.4f\n", cfg.deadzone_size or 0.03))
    file:write(string.format("auto_coord_gain=%.4f\n", cfg.auto_coord_gain or 0.40))
    file:write(string.format("coord_bank_limit=%.2f\n", cfg.coord_bank_limit or 35.0))
    file:write(string.format("damper_gain=%.4f\n", cfg.damper_gain or 0.30))
    file:write(string.format("damper_sensitivity=%.4f\n", cfg.damper_sensitivity or 2.0))
    file:write(string.format("noise_filter=%.4f\n", cfg.noise_filter or 0.05))
    file:write(string.format("timestamp=%d\n", os.time()))
    file:write(string.format("frame=%d\n", state_frame or 0))

    file:close()
end

-- ---------------------------------------------------------------------------
-- Command reader — reads commands.txt and applies them
-- ---------------------------------------------------------------------------
local function read_commands()
    local file = io.open(commands_file, "r")
    if not file then return end

    local commands = {}
    for line in file:lines() do
        line = line:match("^%s*(.-)%s*$")  -- trim
        if line ~= "" and not line:match("^#") then
            table.insert(commands, line)
        end
    end
    file:close()

    -- Clear the commands file after reading
    local clear = io.open(commands_file, "w")
    if clear then clear:close() end

    -- Process each command
    for _, cmd in ipairs(commands) do
        local action, key, value = cmd:match("^(%S+)%s+(%S+)%s*(.*)")

        if action == "set" and key and value ~= "" then
            local num = tonumber(value)
            if key == "elevator_trim" and num then
                config.elevator_trim = num
                logMsg(string.format("[AUTO-YAW DECK] Set elevator_trim=%.3f", num))
            elseif key == "aileron_trim" and num then
                config.aileron_trim = num
                logMsg(string.format("[AUTO-YAW DECK] Set aileron_trim=%.3f", num))
            elseif key == "rudder_trim" and num then
                config.rudder_trim = num
                logMsg(string.format("[AUTO-YAW DECK] Set rudder_trim=%.3f", num))
            elseif key == "flap_ratio" and num then
                config.flap_ratio = num
                dr_flap_ratio[0] = num
                logMsg(string.format("[AUTO-YAW DECK] Set flap_ratio=%.3f", num))
            elseif CONFIG_BOOL_KEYS[key] and config then
                config[key] = (value == "true")
                logMsg(string.format("[AUTO-YAW DECK] Set %s=%s", key, tostring(config[key])))
            elseif CONFIG_NUM_KEYS[key] and num and config then
                config[key] = num
                logMsg(string.format("[AUTO-YAW DECK] Set %s=%.4f", key, num))
            elseif CONFIG_STR_KEYS[key] and config then
                config[key] = value
                logMsg(string.format("[AUTO-YAW DECK] Set %s=%s", key, value))
            else
                logMsg(string.format("[AUTO-YAW DECK] Unknown key: %s = %s", key, value))
            end
        elseif action == "action" and key then
            if key == "reset_trims" then
                config.elevator_trim = 0.0
                config.aileron_trim = 0.0
                config.rudder_trim = 0.0
                logMsg("[AUTO-YAW DECK] Trims reset")
            elseif key == "reset_flaps" then
                config.flap_ratio = 0.0
                dr_flap_ratio[0] = 0.0
                logMsg("[AUTO-YAW DECK] Flaps reset")
            end
        end
    end

    -- Persist all config changes to AutoYaw_profiles.cfg
    if #commands > 0 and save_active_profile then
        save_active_profile()
    end
end

-- ---------------------------------------------------------------------------
-- Main loop — runs every frame via FlyWithLua
-- ---------------------------------------------------------------------------
state_frame = 0

function auto_yaw_deck_main()
    state_frame = state_frame + 1

    local ok, err = pcall(function()
        -- Write state every 3 frames (~20Hz at 60fps) to avoid excessive I/O
        if state_frame % 3 == 0 then
            write_state()
        end

        -- Read commands every 6 frames (~10Hz)
        if state_frame % 6 == 0 then
            read_commands()
        end
    end)
    if not ok then
        logMsg("[AUTO-YAW DECK] Frame error: " .. tostring(err))
    end
end

-- Register with FlyWithLua
do_every_frame("auto_yaw_deck_main()")

logMsg("[AUTO-YAW DECK] Bridge script loaded — state writes to " .. state_file)
logMsg("[AUTO-YAW DECK] Commands read from " .. commands_file)
