## Quick Start (Cross-Platform Setup)

We use **`uv`** as our Python package and project manager. `uv` handles Python installations, virtual environments, and dependency synchronization automatically on Windows, macOS, and Linux.

### 1. Install `uv`

  ```powershell
https://docs.astral.sh/uv/getting-started/installation/
  ```

### 2. Example

`uv` will automatically download the correct Python version (defined in `.python-version`), create a virtual environment, install the dependencies, and run the app with one single command.



```bash
uv run streamlit run src/python_conversational_agent/interface/app.py
```