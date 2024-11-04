module("AircraftList", package.seeall)

--- @class AircraftList
--- @field ALL_PLAYABLE_AIRCRAFT string[]
--- @field CLICKABLE_COCKPIT_AIRCRAFT string[]
--- @field FLAMING_CLIFFS_AIRCRAFT string[]
local AircraftList = {
	ALL_PLAYABLE_AIRCRAFT = {},
	CLICKABLE_COCKPIT_AIRCRAFT = {},
	FLAMING_CLIFFS_AIRCRAFT = {},
}

--- Adds an aircraft to the list of all aircraft
--- @param name string the name of the aircraft as exported from DCS
--- @param has_clickable_cockpit boolean whether the aircraft has a clickable cockpit (if false, it will be exported with FC3 aircraft)
local function add(name, has_clickable_cockpit)
	table.insert(AircraftList.ALL_PLAYABLE_AIRCRAFT, name)
	if has_clickable_cockpit then
		table.insert(AircraftList.CLICKABLE_COCKPIT_AIRCRAFT, name)
	else
		table.insert(AircraftList.FLAMING_CLIFFS_AIRCRAFT, name)
	end
end

add("MosquitoFBMkVI", true)

return AircraftList
