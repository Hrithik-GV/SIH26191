# AI & Machine Learning Pipeline

This module houses the machine learning models and training pipelines for:
1. Multi-hazard vulnerability assessment (flood, landslide, earthquake susceptibility).
2. Habitation carrying capacity estimation models.
3. Relocation urgency & prioritization scoring (multi-criteria decision scoring + supervised ranking).

## Structure:
- `models/`: Serialized model weights and artifacts.
- `training/`: Training scripts and hyperparameter tuning pipelines (Scikit-Learn, XGBoost).
- `features/`: Feature engineering scripts (slope, drainage density, proximity to hazard zones, building density).
- `notebooks/`: Exploratory data analysis and model validation Jupyter notebooks.
