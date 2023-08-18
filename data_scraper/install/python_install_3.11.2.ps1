# Define the URL for Python 3.11.2 installer
$pythonUrl = "https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe"

# Define the installation directory for Python
$installDir = "C:\Python3112"

# Define the path where Python will be added to the system environment variables
$envPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";$installDir"

# Download Python installer
$pythonInstaller = Join-Path $env:TEMP "python-3.11.2-installer.exe"
Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller

# Install Python
Start-Process -Wait -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "TargetDir=$installDir"

# Update the system PATH environment variable
[System.Environment]::SetEnvironmentVariable("Path", $envPath, "Machine")

# Notify user
Write-Host "Python 3.11.2 has been installed and its path has been added to the system environment variables."
