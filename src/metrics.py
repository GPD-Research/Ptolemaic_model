import numpy as np

def angular_residuals(observed_angles, predicted_angles):
    """
    Computes the shortest angular difference between observed and predicted longitudes.
    Essential for circular data to handle the 360 -> 0 wraparound.
    """
    diff = observed_angles - predicted_angles
    return (diff + 180) % 360 - 180

def max_angular_error(observed_angles, predicted_angles):
    """
    The worst-case scenario metric. Historically, a model was often judged by 
    its maximum deviation during critical events, like planetary oppositions.
    """
    residuals = angular_residuals(observed_angles, predicted_angles)
    return np.max(np.abs(residuals))

def mean_absolute_angular_error(observed_angles, predicted_angles):
    """
    Answers the classical question: 'On average, how many degrees off is the 
    prediction from the naked-eye observation?'
    """
    residuals = angular_residuals(observed_angles, predicted_angles)
    return np.mean(np.abs(residuals))

def calculate_chi_squared(observed_angles, predicted_angles, measurement_errors):
    """
    Modern goodness-of-fit. 
    measurement_errors could be set to the naked-eye resolution limit 
    (roughly 1 arcminute, or ~0.016 degrees) or the specific uncertainty 
    of the historical instrument used to log the data.
    """
    residuals = angular_residuals(observed_angles, predicted_angles)
    return np.sum((residuals / measurement_errors) ** 2)

def calculate_aic(chi_squared, num_params):
    """
    Akaike Information Criterion.
    Penalizes 'epicycle stacking'. A base deferent-epicycle system uses ~4 parameters. 
    Adding a minor epicycle adds 2-3 more. AIC will numerically flag this as overfitting 
    when compared to a simpler, unified framework.
    """
    return chi_squared + 2 * num_params

def evaluate_kinematic_model(observed, predicted, errors, num_params):
    """
    Returns a unified dictionary of all metrics to render in the IDE UI.
    """
    chi2 = calculate_chi_squared(observed, predicted, errors)
    return {
        "max_angular_error_deg": max_angular_error(observed, predicted),
        "mean_absolute_error_deg": mean_absolute_angular_error(observed, predicted),
        "chi_squared": chi2,
        "aic": calculate_aic(chi2, num_params)
    }
