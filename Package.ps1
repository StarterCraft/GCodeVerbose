.\.venv\Scripts\Activate.ps1
pyinstaller --name "GCodeVerbose" -F --console .\main.py
Copy-Item ".\dist\GCodeVerbose.exe" -Destination "C:\Program Files\Python311\Scripts"
