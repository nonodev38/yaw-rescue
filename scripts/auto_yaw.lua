-- AUTO-YAW MANAGER

logMsg("[AUTOYAW] Loading active script")

if not SUPPORTS_FLOATING_WINDOWS then
    logMsg("[AUTOYAW] Floating windows are not supported")
    return
end

-- Global (not local) so auto_yaw_deck.lua can read/write it for remote control.
config = {
    enabled = true,
    smoothing_enabled = true,
    deadzone_enabled = true,
    auto_coord_enabled = true,
    yaw_damper_enabled = true,
    smoothing_factor = 0.15,
    deadzone_size = 0.03,
    auto_coord_gain = 0.40,
    coord_bank_limit = 35.0,
    damper_gain = 0.30,
    damper_sensitivity = 2.0,
    noise_filter = 0.05,
    lang = "fr",
    max_output = 1.0,
    elevator_trim = 0.0,
    aileron_trim = 0.0,
    rudder_trim = 0.0,
    flap_ratio = 0.0,
    debug_logging = true,
    debug_interval = 300,
}

local keys = {
    "enabled", "smoothing_enabled", "deadzone_enabled",
    "auto_coord_enabled", "yaw_damper_enabled", "smoothing_factor", "noise_filter",
    "deadzone_size", "auto_coord_gain", "coord_bank_limit",
    "damper_gain", "damper_sensitivity", "max_output",
    "elevator_trim", "aileron_trim", "rudder_trim",
    "flap_ratio", "lang",
    "debug_logging", "debug_interval",
}

-- Load translations
dofile(SCRIPT_DIRECTORY .. "Auto Yaw Deck/translations.lua")

local profiles_path = SCRIPT_DIRECTORY .. "AutoYaw_profiles.cfg"
local profiles = {}
local current_profile = "Default"
local active_aircraft = nil
local pending_aircraft = nil
local pending_frames = 0
local debug_lines = {}
local auto_yaw_wnd = nil

-- Global (not local) so auto_yaw_deck.lua can read computed values for remote control.
state = {
    smoothed_input = 0.0,
    raw_input = 0.0,
    previous_raw = 0.0,
    previous_heading = nil,
    yaw_rate = 0.0,
    yaw_rate_filtered = 0.0,
    bank_angle = 0.0,
    auto_coord_output = 0.0,
    damper_output = 0.0,
    final_output = 0.0,
    frame_count = 0,
    override_active = false,
    last_error = "",
}

local dr_axis = dataref_table("sim/joystick/joy_mapped_axis_value")
local dr_override = dataref_table("sim/operation/override/override_joystick", "writable")
local dr_pitch = dataref_table("sim/joystick/yoke_pitch_ratio", "writable")
local dr_roll = dataref_table("sim/joystick/yoke_roll_ratio", "writable")
local dr_yaw = dataref_table("sim/joystick/yoke_heading_ratio", "writable")
local dr_phi = dataref_table("sim/flightmodel/position/phi")
local dr_psi = dataref_table("sim/flightmodel/position/psi")
local dr_aircraft = dataref_table("sim/aircraft/view/acf_descrip")
local dr_flap_ratio = dataref_table("sim/cockpit2/controls/flap_ratio", "writable")
-- NOTE: trim values are NOT written to trim datarefs.
-- Instead they are applied as direct offsets to dr_pitch/dr_roll/dr_yaw in process_outputs().
-- This works on ALL aircraft, including those without trim tabs (e.g. Cessna 172).

local function add_debug_line(message)
    table.insert(debug_lines, message)
    while #debug_lines > 20 do
        table.remove(debug_lines, 1)
    end
end

local function write_log(message)
    add_debug_line(message)
    logMsg(message)
end

local function clamp(value, minimum, maximum)
    return math.max(minimum, math.min(maximum, value))
end

local function normalize_name(value)
    return string.match(tostring(value or ""), "^%s*(.-)%s*$")
end

local function copy_config_to_profile(name)
    profiles[name] = profiles[name] or {}
    for _, key in ipairs(keys) do
        profiles[name][key] = config[key]
    end
end

local function encode_value(value)
    if type(value) == "boolean" then
        return value and "true" or "false"
    end
    return tostring(value)
end

local function save_profiles()
    local file = io.open(profiles_path, "w")
    if not file then
        write_log("[AUTOYAW] ERROR: Cannot write AutoYaw_profiles.cfg")
        return false
    end

    local names = {}
    for name, _ in pairs(profiles) do
        table.insert(names, name)
    end
    table.sort(names)

    for _, name in ipairs(names) do
        file:write("[" .. name .. "]\n")
        for _, key in ipairs(keys) do
            if profiles[name][key] ~= nil then
                file:write(key .. "=" .. encode_value(profiles[name][key]) .. "\n")
            end
        end
        file:write("\n")
    end
    file:close()
    return true
end

local function parsed_value(key, value)
    if config[key] == nil then
        return nil
    end
    if value == "true" then
        return true
    end
    if value == "false" then
        return false
    end
    return tonumber(value)
end

local function load_profiles()
    local file = io.open(profiles_path, "r")
    if file then
        local section = nil
        for line in file:lines() do
            local header = string.match(line, "^%[%s*(.-)%s*%]$")
            if header then
                section = normalize_name(header)
                profiles[section] = profiles[section] or {}
            else
                local key, value = string.match(line, "^([%w_]+)%s*=%s*(.-)%s*$")
                if section and key and value then
                    local parsed = parsed_value(key, value)
                    if parsed ~= nil then
                        profiles[section][key] = parsed
                    end
                end
            end
        end
        file:close()
    end

    profiles.Default = profiles.Default or {}
    for _, key in ipairs(keys) do
        if profiles.Default[key] == nil then
            profiles.Default[key] = config[key]
        end
    end
    write_log("[AUTOYAW] Profiles loaded")
end

local function apply_profile(name)
    local profile = profiles[name]
    if not profile then
        name = "Default"
        profile = profiles.Default
    end

    current_profile = name
    for _, key in ipairs(keys) do
        if profile[key] ~= nil then
            config[key] = profile[key]
        elseif profiles.Default[key] ~= nil then
            config[key] = profiles.Default[key]
        end
    end
    dr_flap_ratio[0] = config.flap_ratio
    state.previous_heading = nil
    write_log(string.format(
        "[AUTOYAW] Profile applied: %s smoothing=%.3f deadzone=%.3f",
        name, config.smoothing_factor, config.deadzone_size
    ))
end

-- Global (not local) so auto_yaw_deck.lua can call it to persist config changes.
function save_active_profile()
    local name = active_aircraft or current_profile
    if name == "" then
        name = "Default"
    end
    copy_config_to_profile(name)
    current_profile = name
    save_profiles()
    write_log(string.format(
        "[AUTOYAW] Autosave target=%s smoothing=%.3f deadzone=%.3f",
        name, config.smoothing_factor, config.deadzone_size
    ))
end

local function set_value(key, value)
    if config[key] ~= value then
        config[key] = value
        if key == "flap_ratio" then
            dr_flap_ratio[0] = value
        end
        -- trim values (elevator_trim, aileron_trim, rudder_trim) are applied
        -- as offsets to dr_pitch/dr_roll/dr_yaw in process_outputs(),
        -- so no dataref write is needed here.
        save_active_profile()
    end
end

local function make_new_profile(name)
    profiles[name] = {}
    for _, key in ipairs(keys) do
        profiles[name][key] = profiles.Default[key]
    end
    save_profiles()
    write_log("[AUTOYAW] New profile created: " .. name)
end

local function ensure_profile(name)
    if not profiles[name] then
        make_new_profile(name)
    end
    return profiles[name]
end

local function detect_aircraft()
    local name = normalize_name(dr_aircraft[0])
    if name == "" then
        return
    end

    if active_aircraft == nil then
        active_aircraft = name
        pending_aircraft = nil
        pending_frames = 0
        ensure_profile(name)
        apply_profile(name)
        return
    end

    if active_aircraft == name then
        pending_aircraft = nil
        pending_frames = 0
        return
    end

    if pending_aircraft ~= name then
        pending_aircraft = name
        pending_frames = 1
        return
    end

    pending_frames = pending_frames + 1
    if pending_frames < 10 then
        return
    end

    active_aircraft = name
    pending_aircraft = nil
    pending_frames = 0
    ensure_profile(name)
    apply_profile(name)
end

function release_auto_yaw_override()
    if state.override_active then
        dr_override[0] = 0
        state.override_active = false
    end
end

local function process_input()
    local raw = dr_axis[3] or 0.0
    state.raw_input = raw
    -- Noise filter: reject rapid oscillations near center.
    -- If the raw value jumps by more than noise_filter in one frame,
    -- it's likely joystick jitter (physically impossible movement).
    -- In that case, hold the previous smoothed value.
    if config.noise_filter > 0 then
        local delta = math.abs(raw - state.previous_raw)
        if delta > config.noise_filter then
            -- Too rapid change: keep previous smoothed value
            state.previous_raw = raw
            return
        end
    end
    state.previous_raw = raw
    if config.smoothing_enabled then
        state.smoothed_input = config.smoothing_factor * raw
            + (1.0 - config.smoothing_factor) * state.smoothed_input
    else
        state.smoothed_input = raw
    end

    if config.deadzone_enabled then
        local absolute = math.abs(state.smoothed_input)
        if absolute < config.deadzone_size then
            state.smoothed_input = 0.0
        else
            local direction = state.smoothed_input > 0 and 1.0 or -1.0
            state.smoothed_input = direction
                * (absolute - config.deadzone_size)
                / (1.0 - config.deadzone_size)
        end
    end
end

local function process_yaw_rate()
    local heading = dr_psi[0] or 0.0
    if state.previous_heading == nil then
        state.previous_heading = heading
        return
    end
    local delta = heading - state.previous_heading
    while delta > 180.0 do delta = delta - 360.0 end
    while delta < -180.0 do delta = delta + 360.0 end
    local rate = delta * 60.0
    if math.abs(rate) > 180.0 then rate = 0.0 end
    local alpha = clamp(config.damper_sensitivity * 0.05, 0.01, 0.5)
    state.yaw_rate_filtered = alpha * rate
        + (1.0 - alpha) * state.yaw_rate_filtered
    state.yaw_rate = rate
    state.previous_heading = heading
end

local function process_outputs()
    state.bank_angle = dr_phi[0] or 0.0
    state.auto_coord_output = 0.0
    if config.auto_coord_enabled and math.abs(state.bank_angle) >= 1.0 then
        local direction = state.bank_angle > 0 and 1.0 or -1.0
        state.auto_coord_output = direction
            * clamp(math.abs(state.bank_angle) / config.coord_bank_limit, 0.0, 1.0)
            * config.auto_coord_gain
    end

    state.damper_output = 0.0
    if config.yaw_damper_enabled then
        state.damper_output = clamp(
            -(state.yaw_rate_filtered / 30.0) * config.damper_gain,
            -0.5, 0.5
        )
    end

    local output = state.smoothed_input
        + state.auto_coord_output + state.damper_output
    state.final_output = clamp(output, -config.max_output, config.max_output)

    if config.enabled then
        dr_override[0] = 1
        state.override_active = true
        -- Apply trim offsets directly to control surfaces.
        -- elevator_trim offsets pitch, aileron_trim offsets roll, rudder_trim offsets yaw.
        -- This works universally, even on aircraft without trim tabs.
        local pitch_out = (dr_axis[1] or 0.0) + config.elevator_trim
        local roll_out  = (dr_axis[2] or 0.0) + config.aileron_trim
        local yaw_out   = state.final_output + config.rudder_trim
        dr_pitch[0] = clamp(pitch_out, -1.0, 1.0)
        dr_roll[0]  = clamp(roll_out, -1.0, 1.0)
        dr_yaw[0]   = clamp(yaw_out, -config.max_output, config.max_output)
    else
        release_auto_yaw_override()
    end
end

function auto_yaw_main()
    state.frame_count = state.frame_count + 1
    detect_aircraft()

    local ok, error_message = pcall(function()
        process_input()
        process_yaw_rate()
        process_outputs()
    end)

    if not ok then
        state.last_error = tostring(error_message)
        release_auto_yaw_override()
        if state.frame_count <= 10 then
            write_log("[AUTOYAW] Frame error: " .. state.last_error)
        end
        return
    end
    state.last_error = ""

    if state.frame_count % 60 == 0 then
        write_log(string.format(
            "[AUTOYAW] HEARTBEAT frame=%d aircraft=%s profile=%s",
            state.frame_count, tostring(active_aircraft or ""), current_profile
        ))
    end
end

local function draw_section(title, red, green, blue)
    imgui.Separator()
    imgui.TextColored(red, green, blue, 1.0, title)
end

local function draw_checkbox(label, key)
    local changed, value = imgui.Checkbox(label, config[key])
    if changed then
        set_value(key, value)
    end
end

local function draw_slider(label, key, minimum, maximum, format, step)
    step = step or (maximum - minimum) / 100.0
    local value = config[key]

    if imgui.Button("<##" .. key, 24, 22) then
        set_value(key, clamp(value - step, minimum, maximum))
    end
    imgui.SameLine()
    imgui.PushItemWidth(250)
    local changed, slider_value = imgui.SliderFloat(label, config[key], minimum, maximum, format)
    if changed then
        set_value(key, slider_value)
    end
    imgui.PopItemWidth()
    imgui.SameLine()
    if imgui.Button(">##" .. key, 24, 22) then
        set_value(key, clamp(config[key] + step, minimum, maximum))
    end
end

local function draw_resettable_slider(label, key, minimum, maximum, format, step)
    draw_slider(label, key, minimum, maximum, format, step)
    imgui.SameLine()
    if imgui.Button(L("trim_reset") .. "##" .. key, 42, 22) then
        set_value(key, 0.0)
    end
end

function auto_yaw_build(wnd, x, y)
    local ok, error_message = pcall(function()
        imgui.TextColored(0.6, 0.85, 1.0, 1.0, L("title"))
        imgui.SameLine()
        imgui.TextColored(
            config.enabled and 0.2 or 1.0,
            config.enabled and 1.0 or 0.3,
            0.3,
            1.0,
            config.enabled and L("active") or L("inactive")
        )
        imgui.SameLine()
        if imgui.Button(L("lang_btn") .. "##lang", 30, 20) then
            toggle_lang()
        end

        draw_checkbox(L("enable_plugin"), "enabled")

        draw_section(L("smoothing"), 1.0, 0.8, 0.35)
        draw_checkbox(L("enable_smooth") .. "##smooth", "smoothing_enabled")
        draw_slider(L("smooth_factor"), "smoothing_factor", 0.01, 0.50, "%.3f", 0.01)

        draw_section(L("noise"), 1.0, 0.8, 0.35)
        draw_slider(L("noise_threshold"), "noise_filter", 0.0, 0.30, "%.3f", 0.01)

        draw_section(L("deadzone"), 1.0, 0.8, 0.35)
        draw_checkbox(L("enable_deadzone") .. "##deadzone", "deadzone_enabled")
        draw_slider(L("deadzone_size"), "deadzone_size", 0.0, 0.20, "%.3f", 0.01)

        draw_section(L("autocoord"), 1.0, 0.8, 0.35)
        draw_checkbox(L("enable_autocoord"), "auto_coord_enabled")
        draw_slider(L("coord_gain"), "auto_coord_gain", 0.0, 1.0, "%.3f", 0.01)
        draw_slider(L("bank_limit"), "coord_bank_limit", 5.0, 60.0, "%.1f", 1.0)

        draw_section(L("damper"), 1.0, 0.8, 0.35)
        draw_checkbox(L("enable_damper"), "yaw_damper_enabled")
        draw_slider(L("damper_gain"), "damper_gain", 0.0, 1.0, "%.3f", 0.01)
        draw_slider(L("damper_sens"), "damper_sensitivity", 0.5, 5.0, "%.2f", 0.1)

        draw_section(L("trim"), 0.8, 0.65, 1.0)
        draw_resettable_slider(L("trim_pitch"), "elevator_trim", -1.0, 1.0, "%.3f", 0.01)
        draw_resettable_slider(L("trim_roll"), "aileron_trim", -1.0, 1.0, "%.3f", 0.01)
        draw_resettable_slider(L("trim_yaw"), "rudder_trim", -1.0, 1.0, "%.3f", 0.01)

        draw_section(L("flaps"), 0.8, 0.65, 1.0)
        draw_resettable_slider(L("flap_pos"), "flap_ratio", 0.0, 1.0, "%.3f", 0.01)

        draw_section(L("profile"), 0.55, 0.85, 1.0)
        imgui.TextUnformatted(L("aircraft_label") .. tostring(active_aircraft or ""))
        local names = {}
        for name, _ in pairs(profiles) do table.insert(names, name) end
        table.sort(names)
        local selected = 1
        for index, name in ipairs(names) do
            if name == current_profile then selected = index end
        end
        imgui.PushItemWidth(380)
        if imgui.BeginCombo(L("profile_label"), names[selected] or "Default") then
            for index, name in ipairs(names) do
                if imgui.Selectable(name, index == selected) then
                    apply_profile(name)
                end
            end
            imgui.EndCombo()
        end
        imgui.PopItemWidth()

        draw_section(L("telemetry"), 0.4, 0.9, 1.0)
        imgui.TextUnformatted(string.format(L("tel_bank"), state.bank_angle, state.yaw_rate))
        imgui.TextUnformatted(string.format(L("tel_input"), state.raw_input, state.final_output))
        imgui.TextUnformatted(string.format(L("tel_coord"), state.auto_coord_output, state.damper_output))
    end)
    if not ok then
        logMsg("[AUTOYAW] UI error: " .. tostring(error_message))
    end
end

function auto_yaw_on_close(wnd)
    auto_yaw_wnd = nil
end

function toggle_auto_yaw_panel()
    if auto_yaw_wnd then
        float_wnd_destroy(auto_yaw_wnd)
        auto_yaw_wnd = nil
    else
        auto_yaw_wnd = float_wnd_create(520, 850, 1, true)
        float_wnd_set_title(auto_yaw_wnd, "AUTO-YAW MANAGER")
        float_wnd_set_imgui_builder(auto_yaw_wnd, "auto_yaw_build")
        float_wnd_set_onclose(auto_yaw_wnd, "auto_yaw_on_close")
    end
end

function toggle_auto_yaw()
    set_value("enabled", not config.enabled)
    if not config.enabled then release_auto_yaw_override() end
end

function reset_auto_yaw()
    local defaults = {
        enabled = true,
        smoothing_enabled = true,
        deadzone_enabled = true,
        auto_coord_enabled = true,
        yaw_damper_enabled = true,
        smoothing_factor = 0.15,
        deadzone_size = 0.03,
        auto_coord_gain = 0.40,
        coord_bank_limit = 35.0,
        damper_gain = 0.30,
        damper_sensitivity = 2.0,
        noise_filter = 0.05,
        lang = "fr",
        max_output = 1.0,
        elevator_trim = 0.0,
        aileron_trim = 0.0,
        rudder_trim = 0.0,
        flap_ratio = 0.0,
    }
    for key, value in pairs(defaults) do config[key] = value end
    state.smoothed_input = 0.0
    state.previous_raw = 0.0
    state.previous_heading = nil
    state.yaw_rate = 0.0
    state.yaw_rate_filtered = 0.0
    release_auto_yaw_override()
    save_active_profile()
end

load_profiles()
detect_aircraft()
do_every_frame("auto_yaw_main()")
do_on_exit("release_auto_yaw_override()")

auto_yaw_wnd = float_wnd_create(520, 850, 1, true)
float_wnd_set_title(auto_yaw_wnd, "AUTO-YAW MANAGER")
float_wnd_set_imgui_builder(auto_yaw_wnd, "auto_yaw_build")
float_wnd_set_onclose(auto_yaw_wnd, "auto_yaw_on_close")

create_command("plugin/auto_yaw/toggle_panel", "Auto-Yaw: Toggle panel", "toggle_auto_yaw_panel()", "", "")
create_command("plugin/auto_yaw/toggle_plugin", "Auto-Yaw: Toggle plugin", "toggle_auto_yaw()", "", "")
create_command("plugin/auto_yaw/reset", "Auto-Yaw: Reset", "reset_auto_yaw()", "", "")
add_macro("Auto-Yaw: ouvrir/fermer le panneau", "toggle_auto_yaw_panel()")

logMsg("[AUTOYAW] Active script loaded")
