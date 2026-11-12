@echo off
cd /d "%~dp0"
if exist "C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1111-570-0_26.1111.570.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe" (
  "C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1111-570-0_26.1111.570.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe" -m unittest discover -s tests -p "test_*.py" -v
) else (
  py -3 -m unittest discover -s tests -p "test_*.py" -v
)
pause
