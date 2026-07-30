import numpy as np


def calculate_epicycle_path(t_array, R, r, omega_d, omega_e):
    """
    Computes the 2D Cartesian coordinates of a planet over time
    using a standard Deferent-Epicycle model (Earth at 0,0).

    t_array: Array of time steps
    R: Radius of the deferent
    r: Radius of the epicycle
    omega_d: Angular velocity of the deferent center
    omega_e: Angular velocity of the planet on the epicycle
    """
    # Deferent position (center of the epicycle)
    x_d = R * np.cos(omega_d * t_array)
    y_d = R * np.sin(omega_d * t_array)

    # Epicycle displacement
    x_e = r * np.cos(omega_e * t_array)
    y_e = r * np.sin(omega_e * t_array)

    # Total position vector
    x = x_d + x_e
    y = y_d + y_e

    return x, y


def apply_eccentric_earth(x, y, d_x, d_y):
    """
    Shifts the coordinate system so Earth is offset from the
    geometric center of the deferent by distance (d_x, d_y).
    """
    return x - d_x, y - d_y


def calculate_apparent_distance(x, y):
    """
    Returns the scalar distance from Earth (0,0) to the planet.
    Used to model apparent diameter and brightness.
    """
    return np.sqrt(x**2 + y**2)
