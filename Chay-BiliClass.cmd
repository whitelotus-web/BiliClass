@echo off
setlocal
set BILICLASS_EXPERIMENTAL_TEACHING=0
start "" powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0scripts\run.ps1" --page home
