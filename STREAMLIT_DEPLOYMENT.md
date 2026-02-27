# Streamlit Cloud Deployment

Your app is ready for Streamlit Community Cloud, but Streamlit requires a GitHub repository remote.

## 1. Create a GitHub repo

Create an empty repo on GitHub (for example: `capp-turning-web`).

## 2. Push this project

Run these commands in project root:

```powershell
git init
git add .
git commit -m "Add Streamlit web app for CAPP"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If git was already initialized, skip `git init`.

## 3. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io
2. Click `New app`
3. Select your repo and branch `main`
4. Set `Main file path` to:
   `streamlit_app.py`
5. Click `Deploy`

## 3.1 Runtime and system dependencies (required for OCP)

This project uses OpenCASCADE through `cadquery-ocp`, which must run on a compatible runtime.

- Keep `runtime.txt` in repo root with:
  `python-3.12`
- Keep `packages.txt` in repo root so Linux shared libs are installed for VTK/OCP.

If the app was already deployed on a different runtime, open app settings and reboot/redeploy
after pushing these files.

## 4. Add Gemini key in Streamlit secrets

In Streamlit app settings, add this to Secrets:

```toml
GEMINI_API_KEY = "YOUR_KEY"
LLM_PROVIDER = "gemini"
GEMINI_MODEL = "gemini-2.5-flash"
```

Do not commit API keys to source files.

## 5. OCP health check after deploy

After deployment, run one analysis and verify:

- No red banner saying OCP/OpenCASCADE is unavailable.
- Turning score is not fixed at 45/100 for all models.
- Geometry tab changes axis cues and dimensions per file.

If OCP is still unavailable:

1. Clear cache + reboot app in Streamlit settings.
2. Confirm `runtime.txt` is exactly `python-3.12`.
3. Confirm `requirements.txt` and `packages.txt` are from latest commit.
