.\.venv\Scripts\Activate.ps1
pyinstaller --name "GCodeVerbose" -F --console .\main.py
Copy-Item ".\dist\GCodeVerbose.exe" -Destination "C:\Program Files\Python311\Scripts"
Write-Host "Now go update your GitHub repository release: https://github.com/StarterCraft/GCodeVerbose/releases/latest"
Invoke-Item .\dist
