-- AUTO-YAW DECK - Translations for FlyWithLua imgui panel
-- Usage: dofile(SCRIPT_DIRECTORY .. "Auto Yaw Deck/translations.lua")
-- Access: T.section.key

T = {}

T.fr = {
    -- Header
    title = "YAW RESCUE",
    active = "ACTIF",
    inactive = "INACTIF",

    -- Buttons
    lang_btn = "EN",

    -- Sections
    smoothing = "LISSAGE DU SIGNAL",
    noise = "FILTRE BRUIT",
    deadzone = "ZONE MORTE",
    autocoord = "AUTO-COORDINATION",
    damper = "YAW DAMPER",
    trim = "COMPENSATEURS DE TRIM",
    flaps = "VOLETS",
    profile = "PROFIL AVION",
    telemetry = "TELEMETRIE",

    -- Smoothing
    enable_smooth = "Activer le lissage",
    smooth_factor = "Facteur de lissage",

    -- Noise filter
    noise_threshold = "Seuil anti-bruit",

    -- Dead zone
    enable_deadzone = "Activer la zone morte",
    deadzone_size = "Taille zone morte",

    -- Auto-coordination
    enable_autocoord = "Activer auto-coordination",
    coord_gain = "Gain de coordination",
    bank_limit = "Limite de bank",

    -- Yaw damper
    enable_damper = "Activer yaw damper",
    damper_gain = "Gain du damper",
    damper_sens = "Sensibilite du damper",

    -- Trim
    trim_pitch = "Trim profondeur",
    trim_roll = "Trim aileron",
    trim_yaw = "Trim direction",
    trim_reset = "RaZ",

    -- Flaps
    flap_pos = "Position des volets",

    -- Profile
    aircraft_label = "Avion detecte: ",
    profile_label = "Profil",

    -- Telemetry
    tel_bank = "Bank %.2f | Yaw %.2f",
    tel_input = "Entree %.3f | Sortie %.3f",
    tel_coord = "Coord %.3f | Damper %.3f",

    -- Plugin
    enable_plugin = "Activer le plugin",
}

T.en = {
    -- Header
    title = "YAW RESCUE",
    active = "ACTIVE",
    inactive = "INACTIVE",

    -- Buttons
    lang_btn = "FR",

    -- Sections
    smoothing = "SIGNAL SMOOTHING",
    noise = "NOISE FILTER",
    deadzone = "DEAD ZONE",
    autocoord = "AUTO-COORDINATION",
    damper = "YAW DAMPER",
    trim = "TRIM CONTROLS",
    flaps = "FLAPS",
    profile = "AIRCRAFT PROFILE",
    telemetry = "TELEMETRY",

    -- Smoothing
    enable_smooth = "Enable smoothing",
    smooth_factor = "Smoothing factor",

    -- Noise filter
    noise_threshold = "Noise threshold",

    -- Dead zone
    enable_deadzone = "Enable dead zone",
    deadzone_size = "Dead zone size",

    -- Auto-coordination
    enable_autocoord = "Enable auto-coordination",
    coord_gain = "Coordination gain",
    bank_limit = "Bank limit",

    -- Yaw damper
    enable_damper = "Enable yaw damper",
    damper_gain = "Damper gain",
    damper_sens = "Damper sensitivity",

    -- Trim
    trim_pitch = "Pitch trim",
    trim_roll = "Roll trim",
    trim_yaw = "Yaw trim",
    trim_reset = "Reset",

    -- Flaps
    flap_pos = "Flap position",

    -- Profile
    aircraft_label = "Aircraft: ",
    profile_label = "Profile",

    -- Telemetry
    tel_bank = "Bank %.2f | Yaw %.2f",
    tel_input = "Input %.3f | Output %.3f",
    tel_coord = "Coord %.3f | Damper %.3f",

    -- Plugin
    enable_plugin = "Enable plugin",
}

-- Current language (persisted in config)
if config.lang == nil then config.lang = "fr" end

function L(key)
    local lang_table = T[config.lang] or T.fr
    return lang_table[key] or T.fr[key] or key
end

function toggle_lang()
    config.lang = (config.lang == "fr") and "en" or "fr"
end
