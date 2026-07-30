# Ptolemaic_model

This repository contains a deliberately simplified geocentric (Ptolemaic-style) model for educational use inside physics-IDE.

## Purpose

The code is intentionally set up to demonstrate where an archaic cosmological model fails when compared with modern astronomical reference data.

## Run the educational failure test

```bash
python -m unittest tests/test_educational_failure.py
```

The test passes when the model produces large angular errors, which confirms that the historical model is not accurate under modern observational checks.
