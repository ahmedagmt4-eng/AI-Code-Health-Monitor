# AI-Based Code Health Monitoring System

Graduation project prototype for an AI-based system that monitors selected Python code-health indicators and classifies code samples using a Random Forest model.

## Features

- Python source-code submission through a Flask web interface
- Static analysis using Python AST
- Metrics: lines of code, functions, classes, cyclomatic complexity, duplication, unused variables, nesting, and function length
- Transparent 0–100 heuristic health score
- Random Forest classification: **Healthy** or **Potentially Problematic**
- Issue detection and recommendations
- Functional test cases

## Project structure

```text
AI-Code-Health-Monitor/
├── app.py
├── analyzer.py
├── ai_model.py
├── train_model.py
├── requirements.txt
├── dataset/
│   └── code_health_dataset.csv
├── model/
│   └── random_forest_model.pkl
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   ├── css/style.css
│   └── js/script.js
├── test/
│   └── test_system.py
└── README.md
```

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python train_model.py
python app.py
```

Then open `http://127.0.0.1:5000`.

## Tests

Install pytest if needed, then run:

```bash
pytest -q
```

## Important academic note about the dataset

The included CSV is a **synthetic demonstration dataset** created from an explicit rule so the prototype can run immediately. It should not be presented as an empirical benchmark dataset. For the final academic evaluation, replace it with an appropriate public software-defect/code-quality dataset whose features and labels match the project's research design, then retrain the model and report the resulting test metrics.

The Random Forest model file included in `model/` is trained from the included demonstration dataset. Therefore, its performance should be described as prototype/demo performance unless and until a validated dataset is used.

## Deployment

The repository is structured for GitHub and can be deployed to a Python hosting service such as Render. For a live demonstration, push the repository to GitHub and connect the repository to the hosting service. Use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

If the platform does not provide a persistent filesystem, keep the model file in the repository as included here or retrain it during the build step.

## Project alignment

The prototype implements the core practical workflow described in the project report: user input → code validation → static analysis → AI classification → reporting.
