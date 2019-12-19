# WyscoutAnalyzer
There are programs, notebooks for analysis of Wyscout Dataset

Overview
this project is scrum team of PredictPeopleFlow

Directory Tree
---------------------
    .
    ├── README.md          <- The top-level README for developers using this project.
    │
    ├── data               <- Dataset Dirctory
    │   │
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
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
        ├── main.py                  <- Learn / Predict pipeline
        ├── dataset.py               <- Dataset class
        ├── transformer.py           <- Transformer class
        ├── trainer.py               <- Trainer class（in the future, we rename class）
        ├── logger.py                <- Logger class
        ├── models                   <- Model class Directory
        │   ├── __init__.py
        │   └── model_{LibraryName / MethodType / Author Name}.py     <- Divided by using Librart, Method, Author Name
        │
        └── utils                    <- Utils Directory、Modules diveded by Big Label
            |                           Big Label = math, visualization, ...
            ├── __init__.py
            ├── math_func.py
            └── visualization_func.py
---------------------