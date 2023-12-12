
import logging
MAX_WILDFIRE_CHANCE = 50 
WILDFIRE_MAX_HALF = 0.25
MAX_SPEED = 60 
MIN_SPEED = 15
MAX_TEMP = 110
MIN_TEMP = 80
MAX_HUMD = 30
MIN_HUMD = 10

# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)

def calc_wildfire_risk_stage(fire_chance):
    """
    Find the risk stage from a fire chance percentage 
    """
    stage_1 = 0 
    stage_2 = (1/3) * MAX_WILDFIRE_CHANCE
    stage_3 = (2/3) * MAX_WILDFIRE_CHANCE
    
    if fire_chance >= stage_1 and fire_chance < stage_2:
        return "low "
    elif fire_chance >= stage_2 and fire_chance < stage_3:
        return "moderate"
    elif fire_chance > stage_3:
        return "high risk"



def calc_wildfire_percent_risk(temp_str, wind_str, humd_str): 
    """
    Calculates the risk percentage of a wildfire based on temp, humditiy, and wind speed. 
    Note: The max risk is 50%
    """
    # If none of the risk combos are met, the risk is 0 for today
    temp = float(temp_str)
    wind = float(wind_str)
    humd = float(humd_str)
    
    percent_risk = 0 


    if wind >= MAX_SPEED and temp >= MAX_TEMP: 
        """
        If the wind and temp are higher than the max for it to be considered
        a wildfire condition, we set the wind and temp wildfire risk to max 
        and add them
        """
        wind_risk = WILDFIRE_MAX_HALF
        temp_risk = WILDFIRE_MAX_HALF
        slogger.debug(f"wild calc: cond #1 wind:{wind_risk} | temp:{temp_risk}")
        percent_risk = wind_risk + temp_risk

    elif wind >= MIN_SPEED and temp >= MIN_TEMP: 
        """
        If the wind and temp are higher than the min constraint for a wildfire 
        condition, we calculate their risk factors and add them together
        """
        wind_risk = (wind/MAX_SPEED)*(WILDFIRE_MAX_HALF)
        temp_risk = (temp/MAX_TEMP)*(WILDFIRE_MAX_HALF)
        slogger.debug(f"wild calc: cond #2 wind:{wind_risk} | temp{temp_risk}") 
        percent_risk = wind_risk + temp_risk

    elif wind >= MAX_SPEED and humd <= MIN_HUMD: 
        """
        If the wind is higher the max wildfire constraint and humditity is lower than min 
        constraint, we set the wind and humd widlfire risk to max and add them
        """
        wind_risk = WILDFIRE_MAX_HALF
        humd_risk = WILDFIRE_MAX_HALF
        slogger.debug(f"wild calc: cond #3 wind:{wind_risk} | humd:{humd_risk}")
        percent_risk = wind_risk + humd_risk

    elif wind >= MIN_SPEED and humd <= MAX_HUMD:
        """
        If the wind is higher than min wildfire constraint and humd is lower than max humd 
        before being a wildfire risk, we calculate their risk factors and add them together
        """
        wind_risk = (wind/MAX_SPEED)*(WILDFIRE_MAX_HALF)
        humd_risk = ((MAX_HUMD - humd)/MAX_HUMD)*(WILDFIRE_MAX_HALF)
        slogger.debug(f"wild calc: cond #4 wind:{wind_risk} | humd:{humd_risk}")
        percent_risk = wind_risk + humd_risk
		
    elif temp >= MAX_TEMP and humd <= MIN_HUMD: 
        """
        If the temp is higher than the max wildfire risk constraint and humd is lower than min 
        wildfire risk constraint we set them to the max widlfire risk and add them
        """
        temp_risk = WILDFIRE_MAX_HALF
        humd_risk = WILDFIRE_MAX_HALF
        slogger.debug(f"wild calc: cond #5 temp:{temp_risk} | humd:{humd_risk}")
        percent_risk = temp_risk + humd_risk

    elif temp >= MIN_TEMP and humd <= MAX_HUMD:
        """
        If the temp is higher than min wildfire constraint and humd is lower than max wildfire constraint
        we calculate their risk factors and add them together
        """
        temp_risk = (temp/MAX_TEMP)*(WILDFIRE_MAX_HALF)
        humd_risk = ((MAX_HUMD - humd)/MAX_HUMD)*(WILDFIRE_MAX_HALF)
        slogger.debug(f"wild calc: cond #6 temp:{temp_risk} | humd:{humd_risk}")
        percent_risk = temp_risk + humd_risk

    #Convert the percent_risk to a better whole number rounded to the second decimal place and return it
    percent = round(percent_risk * 100, 2)
    slogger.debug(f"wild calc: return is {percent}")
    return percent