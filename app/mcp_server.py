from mcp.server.fastmcp import FastMCP

mcp = FastMCP("EcoPulse Server")

@mcp.tool()
def get_air_quality(location: str) -> str:
    """Gets the current Air Quality Index (AQI) and pollutant levels for a location.
    
    Args:
        location: The city or region name.
    """
    loc_clean = location.lower()
    if "san francisco" in loc_clean or "sf" in loc_clean:
        return (
            "Location: San Francisco, CA\n"
            "AQI: 42 (Good)\n"
            "PM2.5: 9.8 µg/m³\n"
            "PM10: 15 µg/m³\n"
            "NO2: 12 ppb\n"
            "Ozone: 34 ppb\n"
            "Primary Pollutant: PM2.5\n"
            "Status: Air quality is satisfactory, and air pollution poses little or no risk."
        )
    elif "beijing" in loc_clean:
        return (
            "Location: Beijing, China\n"
            "AQI: 155 (Unhealthy)\n"
            "PM2.5: 63.4 µg/m³\n"
            "PM10: 95 µg/m³\n"
            "NO2: 38 ppb\n"
            "Ozone: 15 ppb\n"
            "Primary Pollutant: PM2.5\n"
            "Status: Active children and adults, and people with respiratory disease, should avoid prolonged outdoor exertion."
        )
    else:
        return (
            f"Location: {location}\n"
            "AQI: 65 (Moderate)\n"
            "PM2.5: 18.2 µg/m³\n"
            "PM10: 28 µg/m³\n"
            "NO2: 15 ppb\n"
            "Ozone: 40 ppb\n"
            "Primary Pollutant: PM2.5\n"
            "Status: Air quality is acceptable; however, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
        )

@mcp.tool()
def get_environmental_report(location: str) -> str:
    """Fetches the latest regional environmental and emissions report.
    
    Args:
        location: The city or region name.
    """
    loc_clean = location.lower()
    if "san francisco" in loc_clean or "sf" in loc_clean:
        return (
            "--- SF Bay Area Environmental Quality Report ---\n"
            "Emissions Trend: Carbon emissions decreased by 2.4% last quarter, driven by increased residential solar uptake and EV registration.\n"
            "Industrial Pollution: Low. Minimal heavy industry, major emissions come from transportation (commuter traffic on HWY 101/80).\n"
            "Key Concerns: Occasional seasonal ozone peaks during late summer; wildfire smoke drift risks in autumn."
        )
    elif "beijing" in loc_clean:
        return (
            "--- Beijing Environmental & Emissions Summary ---\n"
            "Emissions Trend: Particulate levels are high due to industrial coal combustion in surrounding regions and heavy vehicle traffic.\n"
            "Industrial Pollution: Moderate-to-high. Surrounding steel mills and coal-fired plants contribute to regional sulfur and nitrogen dioxide load.\n"
            "Key Concerns: High seasonal smog peaks in winter during heating season; regular dust storms in spring."
        )
    else:
        return (
            f"--- Regional Environmental Profile: {location} ---\n"
            "Emissions Trend: Stable. Transportation and commercial heating remain the primary carbon emission contributors.\n"
            "Industrial Pollution: Moderate. Light manufacturing is compliant with local environmental laws.\n"
            "Key Concerns: General vehicle congestion in downtown core is increasing localized PM2.5 levels."
        )

@mcp.tool()
def get_local_climate_policies(location: str) -> str:
    """Gets the municipal climate policies and active green programs for a location.
    
    Args:
        location: The city or region name.
    """
    loc_clean = location.lower()
    if "san francisco" in loc_clean or "sf" in loc_clean:
        return (
            "--- SF Climate Action Plan Initiatives ---\n"
            "1. SF Zero Waste: Goal of routing 100% of municipal solid waste away from landfills.\n"
            "2. CleanPowerSF: Community Choice Aggregation offering 100% renewable electricity options to businesses/residents.\n"
            "3. Urban Forestry Program: Grants available for street tree planting and volunteer greening groups."
        )
    else:
        return (
            f"--- Municipal Green Policies: {location} ---\n"
            "1. EcoTransit Plan: City offers free park-and-ride shuttle buses on weekends to reduce downtown traffic.\n"
            "2. SaveWatts: Rebates for smart thermostat installations in older residential buildings.\n"
            "3. Community Garden Grant: Residents can apply for municipal land use permissions and seed funding to start community compost/garden sites."
        )

@mcp.tool()
def calculate_emissions_impact(activity_type: str, units: float) -> str:
    """Calculates the carbon footprint impact of personal or community activities.
    
    Args:
        activity_type: Type of action ('carpool', 'solar_power', 'tree_planted', or 'waste_diverted').
        units: Number of miles carpooled, kWh solar produced, trees planted, or lbs waste diverted.
    """
    act = activity_type.lower()
    if "carpool" in act:
        co2_saved = units * 0.404
        return f"Carpooling {units} miles saves approximately {co2_saved:.2f} lbs ({(co2_saved*0.453592):.2f} kg) of CO2 emissions compared to driving alone."
    elif "solar" in act:
        co2_saved = units * 0.85
        return f"Producing {units} kWh of solar electricity saves approximately {co2_saved:.2f} lbs ({(co2_saved*0.453592):.2f} kg) of CO2 emissions from coal/gas grids."
    elif "tree" in act:
        co2_saved = units * 48.0
        return f"Planting {units} trees will absorb approximately {co2_saved:.2f} lbs ({(co2_saved*0.453592):.2f} kg) of CO2 per year once mature."
    elif "waste" in act:
        co2_saved = units * 0.9
        return f"Diverting {units} lbs of compostable/recyclable waste from landfills saves approximately {co2_saved:.2f} lbs ({(co2_saved*0.453592):.2f} kg) of CO2 equivalent emissions."
    else:
        return f"Unknown activity type '{activity_type}'. Supported: 'carpool', 'solar_power', 'tree_planted', 'waste_diverted'."

if __name__ == "__main__":
    mcp.run()
