@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "ROOT=%~dp0"
set "SERVE="
set "MODEL="

if exist "%ROOT%ninfer-serve.exe" set "SERVE=%ROOT%ninfer-serve.exe"
if not defined SERVE if exist "%ROOT%build\apps\ninfer-serve.exe" set "SERVE=%ROOT%build\apps\ninfer-serve.exe"
if not defined SERVE (
  for /r "%ROOT%engine" %%F in (ninfer-serve.exe) do if not defined SERVE set "SERVE=%%~fF"
)
if exist "%ROOT%MODEL_PATH.txt" set /p MODEL=<"%ROOT%MODEL_PATH.txt"
if not defined MODEL if exist "D:\ws\ai\ninfer-huihui\MODEL_PATH.txt" set /p MODEL=<"D:\ws\ai\ninfer-huihui\MODEL_PATH.txt"

if not defined SERVE (
  echo [ERROR] ninfer-serve.exe was not found.
  echo         Build with build_windows.bat, or place the release binary beside this launcher.
  pause
  exit /b 1
)

if not defined MODEL (
  echo [ERROR] MODEL_PATH.txt is missing or empty.
  pause
  exit /b 1
)

if not exist "%MODEL%" (
  echo [ERROR] Model artifact does not exist:
  echo         %MODEL%
  pause
  exit /b 1
)

netstat -ano | findstr ":39217" | findstr /I "LISTENING" >nul 2>&1
if not errorlevel 1 (
  echo [ERROR] Port 39217 is already in use.
  netstat -ano | findstr ":39217"
  pause
  exit /b 1
)

echo Engine: %SERVE%
echo Model:  %MODEL%
echo API:    http://127.0.0.1:39217/v1
echo.

"%SERVE%" "%MODEL%" ^
  --vision ^
  --spec mtp ^
  --draft-tokens 5 ^
  --lm-head-draft ^
  --host 127.0.0.1 ^
  --port 39217 ^
  --model-id qwen3.8-27b-huihui-abliterated ^
  --max-context 262144 ^
  --device-state-slots 1 ^
  --kv-capacity auto ^
  --kv-dtype nvfp4 ^
  --prefill-chunk 4096 ^
  --max-concurrency 1 ^
  --host-state-slots 8 ^
  --host-kv-mib 8192 ^
  --max-shared-prefixes 7 ^
  --max-private-continuations 8 ^
  --max-long-anchors-per-continuation 4 ^
  --preserve-thinking ^
  --default-thinking-budget 4096 ^
  --pending-timeout-ms 600000

echo.
echo NInfer exited with code %ERRORLEVEL%.
pause
