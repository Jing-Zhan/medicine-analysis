@echo off
setlocal

rem ============================================================
rem  Local launcher for the Django big-screen project (Windows)
rem  Uses the offline deps in ..\_deps if present,
rem  otherwise falls back to the Django installed in the current Python.
rem ============================================================

set "ROOT=%~dp0"
set "DEPS=%ROOT%..\_deps"

if exist "%DEPS%\django" (
    set "PYTHONPATH=%DEPS%"
    echo [1/2] using offline deps: %DEPS%
) else (
    echo [1/2] _deps not found, using the Django already installed
)

echo [2/2] starting http://127.0.0.1:8000/
echo       press Ctrl+C to stop
echo.

python "%ROOT%manage.py" runserver 0.0.0.0:8000
pause
