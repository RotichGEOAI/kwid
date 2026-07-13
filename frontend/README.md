# KWID Svelte Micro-Frontend (optional)

This is an optional, buildable Svelte component for a richer animated
header. **The main Streamlit app does not require it** — `components/header.py`
automatically falls back to native Streamlit markup if `frontend/dist/`
does not exist.

## Build

```bash
cd frontend
npm install
npm run build
```

This produces `frontend/dist/index.html`, which `components/header.py`
will detect and embed automatically on the next `streamlit run streamlit_app.py`.
