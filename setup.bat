@echo off
setlocal

cd /d "%~dp0"

py -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt

if not exist gm\config_local.py (
  copy gm\config_local.example.py gm\config_local.py
)

echo.
echo Setup complete.
echo Edit gm\config_local.py with your Jellyfin details.
echo Then run: python -m gm.generate_models_html
echo And start the server with: python server.py
echo.
pause
