## Quick Start

### Requirements
- **Ollama**: [Download and install Ollama](https://ollama.com/)
- **uv**: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Setup and Run

1. **Pull and run the model via Ollama:**
   ```bash
   ollama pull mistral
   ollama run mistral
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/TopiKorhonen/python-conversational-agent.git
   ```

3. **Change into the project directory:**
   ```bash
   cd python-conversational-agent
   ```

4. **Sync dependencies:**
   ```bash
   uv sync
   ```

5. **Run the program:**
   ```bash
   uv run streamlit run src/python_conversational_agent/interface/app.py
   ```