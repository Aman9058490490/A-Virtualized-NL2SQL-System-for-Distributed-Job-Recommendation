# Streamlit Frontend for Federated NL→SQL Demo

This small Streamlit app provides a quick frontend to run `run_demo.py` from
the project and display its console output inside a browser UI.

How to run

1. Activate your existing `shrm` venv (do not create a new venv):

```powershell
E:\path\to\project\shrm\Scripts\Activate.ps1
```

2. Install requirements (if not already installed):

```powershell
python -m pip install -r requirements.txt
```

3. Start Streamlit (from project root):

```powershell
streamlit run streamlit_app.py
```

Notes
- The app runs `run_demo.py` as a subprocess using the same Python
  interpreter that started Streamlit. Ensure Streamlit is launched from
  the `shrm` venv so dependencies (and your `shrm` interpreter) are used.
- The app displays stdout and stderr produced by `run_demo.py`.
