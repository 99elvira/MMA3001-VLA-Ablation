@echo off
cd /d "%~dp0.."
python -m pytest tests -v --html=docs/test_report.html --self-contained-html
if errorlevel 1 exit /b 1
python -m src.analysis
if errorlevel 1 exit /b 1
python -m pdoc src -o docs/api
if errorlevel 1 exit /b 1
