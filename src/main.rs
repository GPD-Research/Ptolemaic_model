use std::error::Error;
use std::path::Path;

use ptolemaic_model_backend::{detect_retrograde_motion, load_observations, mean_absolute_angular_error};

fn main() -> Result<(), Box<dyn Error>> {
    let input_path = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "data/almagest_planetary_logs.csv".to_string());

    let path = Path::new(&input_path);
    let observations = load_observations(path)?;

    let longitudes: Vec<f64> = observations
        .iter()
        .map(|observation| observation.ecliptic_longitude_deg)
        .collect();

    let retrograde_points = detect_retrograde_motion(&longitudes);
    let self_error = mean_absolute_angular_error(&longitudes, &longitudes);

    println!("Loaded {} observations from {}", observations.len(), input_path);
    println!("Retrograde points detected: {}", retrograde_points.len());
    println!("Mean absolute angular error (self-prediction): {:.4}", self_error);

    Ok(())
}
