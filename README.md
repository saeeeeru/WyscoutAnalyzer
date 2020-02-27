# WyscoutAnalyzer
## overview
There are source code for vizualization and notebooks for analysis of Wyscout Dataset

## Directory Tree
---------------------
    .
    ├── README.md          <- The top-level README for developers using this project.
    │
    ├── data               <- Dataset Dirctory
    │   │
    │   ├── raw            <- The original, immutable data dump.
    │   └── processed      <- The final, canonical data sets for modeling.
    │
    ├── notebook          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │   │                     the creator's initials, and a short `-` delimited description, e.g.
    │   │                     `1.0-jqp-initial-data-exploration`.
    │   │
    │   └── {VerificationTitle}        <- each verification title e.g. = Trial3DCNN, VizMap
    │               |
    │               ├── README.md        <- overview markdown file which has Verification Goal, pipeline, environment
    │               └── {Number}-{Name}.ipynb        <- Number means processing step, Name means Processing Title 
    │                                               e.g. = 1.PreprocessingDataset.ipynb, 2-FitModel.ipynb, 
    │                                                      3-VerificatePredictPerformance.ipynb
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    └── src                <- Source code in this project.
        │
        ├── __init__.py
        ├── main.py                  <- main application program
        ├── utils.py                 <- utility functions
        └── viz_func.py              <- vizualization functions
        
---------------------