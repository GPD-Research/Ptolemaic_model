use serde::Deserialize;
use std::error::Error;
use std::fs::File;
use std::path::Path;

#[derive(Debug, Deserialize)]
pub struct Observation {
    pub observation_id: u32,
    pub days_from_epoch: f64,
    pub calendar_date: String,
    pub planet: String,
    pub ecliptic_longitude_deg: f64,
    pub ecliptic_latitude_deg: f64,
    pub historical_source: String,
    pub notes: String,
}

pub fn load_observations(path: &Path) -> Result<Vec<Observation>, Box<dyn Error>> {
    let file = File::open(path)?;
    let mut reader = csv::Reader::from_reader(file);

    let mut observations = Vec::new();
    for record in reader.deserialize() {
        let observation: Observation = record?;
        observations.push(observation);
    }

    Ok(observations)
}

pub fn detect_retrograde_motion(longitudes: &[f64]) -> Vec<f64> {
    let mut retrograde_times = Vec::new();

    for window in longitudes.windows(2) {
        let current = window[0];
        let next = window[1];
        let delta = next - current;

        if delta < 0.0 {
            retrograde_times.push(current);
        }
    }

    retrograde_times
}

pub fn angular_residuals(observed: &[f64], predicted: &[f64]) -> Vec<f64> {
    observed
        .iter()
        .zip(predicted.iter())
        .map(|(obs, pred)| {
            let diff = obs - pred;
            let wrapped = ((diff + 180.0) % 360.0 + 360.0) % 360.0 - 180.0;
            wrapped
        })
        .collect()
}

pub fn mean_absolute_angular_error(observed: &[f64], predicted: &[f64]) -> f64 {
    let residuals = angular_residuals(observed, predicted);
    residuals.iter().map(|value| value.abs()).sum::<f64>() / residuals.len() as f64
}
