# 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd ai-log-forensic
```

# 2. Create Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

# 4. Configure Dataset Paths

Create:

```text
src/config.py
```

Add:

```python
from pathlib import Path

DATA_DIR = Path("data_cert")
```

# 5. Dataset Structure

```text
data_cert/
├── logon.csv
├── device.csv
├── email.csv
├── file.csv
```

# 6. Run ML Pipeline

```bash
python run_ml_pipeline.py
```

# 7. Run Backend

```bash
uvicorn api.main:app --reload
```

API Docs:

```text
http://127.0.0.1:8000/docs
```

# 8. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

# 9. Train Classical ML Models

```bash
python train_and_save_model.py
```

Models trained:

- Logistic Regression
- Random Forest
- Gradient Boosting
- LightGBM

# 10. Run Graph Pipeline

```bash
python test_graph.py
```

# 11. Prepare LSTM Sequences

```bash
python train_lstm_prepare.py
```

# 12. Train LSTM

```bash
python train_lstm.py
```

# 13. Export Reports

Available exports:

- CSV
- PDF
- anomaly summaries
- graph visualizations

# 14. Run on Kaggle

Configure:

```python
from pathlib import Path

DATA_DIR = Path(
    "/kaggle/input/<dataset_name>/data_cert"
)
```

Install:

```python
!pip install lightgbm tensorflow networkx shap
```

# 15. Recommended Execution Order

```bash
python run_ml_pipeline.py
python test_graph.py
python train_lstm_prepare.py
python train_lstm.py
uvicorn api.main:app --reload
npm run dev
```
