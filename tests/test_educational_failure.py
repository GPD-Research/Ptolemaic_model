import unittest
from pathlib import Path

from ptolemaic_model import evaluate_model_errors, load_reference_observations


class EducationalFailureTest(unittest.TestCase):
    def test_ptolemaic_model_fails_against_reference_observations(self) -> None:
        observations = load_reference_observations(
            Path(__file__).resolve().parents[1] / "data" / "reference_observations.csv"
        )
        errors = evaluate_model_errors(observations)

        self.assertGreaterEqual(len(errors), 5)
        self.assertTrue(all(error > 20.0 for error in errors))


if __name__ == "__main__":
    unittest.main()
