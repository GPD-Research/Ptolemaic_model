import numpy as np

def calculate_apparent_longitude(x, y):
    """
    Converts the 2D physical path of the planet into the 
    angular longitude observed from Earth (the origin).
    Returns the angle in degrees (0 to 360).
    """
    angles_radians = np.arctan2(y, x)
    angles_degrees = np.degrees(angles_radians)
    
    # Normalize to 0-360 degrees
    return angles_degrees % 360.0

def detect_retrograde_motion(t_array, apparent_longitudes):
    """
    Analyzes the array of apparent longitudes to find periods 
    where the angular velocity is negative (moving backward in the sky).
    """
    delta_long = np.diff(apparent_longitudes)
    
    # Handle the 360 -> 0 wraparound
    delta_long = np.where(delta_long < -180, delta_long + 360, delta_long)
    delta_long = np.where(delta_long > 180, delta_long - 360, delta_long)
    
    # True where planet is in retrograde
    retrograde_mask = delta_long < 0
    return t_array[:-1][retrograde_mask]
