use std::path::Path;

use ptolemaic_model_backend::{detect_retrograde_motion, load_observations, mean_absolute_angular_error};

#[test]
fn loads_the_planetary_dataset() {
    let path = Path::new("data/almagest_planetary_logs.csv");
    let observations = load_observations(path).expect("dataset should load");

    assert_eq!(observations.len(), 8);
}

#[test]
fn detects_a_retrograde_segment_from_the_dataset() {
    let path = Path::new("data/almagest_planetary_logs.csv");
    let observations = load_observations(path).expect("dataset should load");
    let longitudes: Vec<f64> = observations
        .iter()
        .map(|observation| observation.ecliptic_longitude_deg)
        .collect();

    let retrograde = detect_retrograde_motion(&longitudes);

    assert!(!retrograde.is_empty());
}

#[test]
fn reports_zero_error_when_predictions_match_observations() {
    let values = vec![95.4, 108.1, 111.5, 109.2, 104.5, 99.8, 97.1, 102.3];

    let error = mean_absolute_angular_error(&values, &values);

    assert!(error < 1e-9);
}
