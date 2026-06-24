# LM Studio Gateway Files

These files implement the local LLM gateway for the robot mascot prototype.

## Files included

```text
agent/
  __init__.py
  config.py
  json_utils.py
  lmstudio_client.py
  prompts.py
  schemas.py
app_lmstudio_cli.py
streamlit_lmstudio_demo.py
.env.example
requirements-lmstudio.txt
pyproject.example.toml
docs/lmstudio_gateway.md
tests/test_schemas.py
```

## Recommended git workflow

From your repo root:

```bash
git switch branch-lauri
```

Copy these files into the repo root, then run:

```bash
uv add openai pydantic python-dotenv streamlit
cp .env.example .env
```

Start LM Studio's local server and load a chat/instruct model.

Run the CLI test:

```bash
uv run python app_lmstudio_cli.py
```

Run the Streamlit test:

```bash
uv run streamlit run streamlit_lmstudio_demo.py
```

Commit when it works:

```bash
git add .
git commit -m "Add LM Studio LLM gateway"
git push
```

## Notes

If your team already has a `pyproject.toml`, do not overwrite it with `pyproject.example.toml`. Merge only the dependencies.

If JSON output fails often, use a stronger instruct model in LM Studio. Models around 7B or larger usually follow structured-output instructions better than very small models.
