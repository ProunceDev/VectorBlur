# Check if Python is installed
Write-Host "Checking if Python is installed..."
$pythonInstalled = $false

try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        $pythonInstalled = $true
    }
} catch {}

if (-not $pythonInstalled) {
    Write-Host "Python is not installed. Downloading and installing..."

    # Define Python installer URL and file name
    $pythonUrl = "https://www.python.org/ftp/python/3.12.1/python-3.12.1.exe"
    $installer = "$env:TEMP\python_installer.exe"

    # Download the Python installer
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installer

    # Check if the file was downloaded
    if (-Not (Test-Path $installer)) {
        Write-Host "Failed to download the Python installer."
        exit 1
    }

    # Install Python silently
    Write-Host "Installing Python..."
    Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -NoNewWindow -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") +
                ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
    # Verify installation
    try {
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            Write-Host "Python installation failed."
            exit 1
        }
    } catch {
        Write-Host "Python installation failed."
        exit 1
    }

    Write-Host "Python installed successfully."
    Remove-Item $installer -Force
} else {
    Write-Host "Python is already installed."
}
# Check and install required Python packages
Write-Host "Checking required Python packages..."

$requiredPackages = @("customtkinter", "cv2")  # Check for cv2 instead of opencv-python
$installPackages = @("customtkinter", "opencv-python")  # Install as opencv-python

$missingPackages = @()

for ($i = 0; $i -lt $requiredPackages.Length; $i++) {
    $pkg = $requiredPackages[$i]
    $installPkg = $installPackages[$i]

    $check = python -c "import importlib.util; print(importlib.util.find_spec('$pkg') is not None)" 2>$null
    if ($check -ne "True") {
        $missingPackages += $installPkg
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "Installing missing packages: $($missingPackages -join ', ')"
    python -m pip install $missingPackages
} else {
    Write-Host "All required packages are installed."
}


Write-Host "Checking if Blur is installed..."
# Check if Blur is installed
$blurPath = "C:\Program Files (x86)\blur\blur.exe"
if (-Not (Test-Path $blurPath)) {
    Write-Host "Blur is not installed. Downloading and installing..."

    # Define Blur installer URL and file name
    $blurUrl = "https://github.com/f0e/blur/releases/download/v1.8/blur-installer.exe"
    $blurInstaller = "$env:TEMP\blur-installer.exe"

    # Download Blur installer
    Invoke-WebRequest -Uri $blurUrl -OutFile $blurInstaller

    # Check if the file was downloaded
    if (-Not (Test-Path $blurInstaller)) {
        Write-Host "Failed to download the Blur installer."
        exit 1
    }

    # Install Blur
    Write-Host "Installing Blur..."
    Start-Process -FilePath $blurInstaller -ArgumentList "/SILENT" -NoNewWindow -Wait

    # Verify installation
    if (-Not (Test-Path $blurPath)) {
        Write-Host "Blur installation failed."
        exit 1
    }

    Write-Host "Blur installed successfully."
    Remove-Item $blurInstaller -Force
} else {
    Write-Host "Blur is already installed."
}

Write-Host "Setup complete."

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

Write-Host "Running VectorBlur..."
python main.py
