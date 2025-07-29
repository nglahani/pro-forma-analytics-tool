# Windows Task Scheduler Setup for Pro Forma Data Updates
# Run this script as Administrator to setup automated data updates

param(
    [string]$ProjectPath = "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool",
    [string]$PythonPath = "python",
    [string]$FredApiKey = ""
)

Write-Host "Setting up Windows Task Scheduler for Pro Forma Data Updates" -ForegroundColor Green

# Function to create a scheduled task
function Create-DataUpdateTask {
    param(
        [string]$TaskName,
        [string]$Schedule,
        [string]$StartTime,
        [string]$ScriptArgs
    )
    
    Write-Host "Creating task: $TaskName" -ForegroundColor Yellow
    
    # Create the action
    $Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptArgs -WorkingDirectory $ProjectPath
    
    # Create the trigger based on schedule
    switch ($Schedule) {
        "Daily" {
            $Trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
        }
        "Weekly" {
            $Trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday -At $StartTime
        }
        "Monthly" {
            $Trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 4 -DaysOfWeek Monday -At $StartTime
        }
    }
    
    # Create settings
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    # Create the principal (run as current user)
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    
    # Register the task
    try {
        Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force
        Write-Host "✓ Task '$TaskName' created successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to create task '$TaskName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Validate paths
if (-not (Test-Path $ProjectPath)) {
    Write-Host "Error: Project path does not exist: $ProjectPath" -ForegroundColor Red
    exit 1
}

# Test Python installation
try {
    $PythonVersion = & $PythonPath --version 2>&1
    Write-Host "Using Python: $PythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python not found at '$PythonPath'. Please install Python or update the path." -ForegroundColor Red
    exit 1
}

# Setup environment variable for FRED API key if provided
if ($FredApiKey -ne "") {
    Write-Host "Setting FRED_API_KEY environment variable" -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("FRED_API_KEY", $FredApiKey, "User")
}

# Create scheduled tasks for different update frequencies

Write-Host "`nCreating scheduled tasks..." -ForegroundColor Yellow

# Weekly updates for interest rates (Mondays at 2:00 AM)
$WeeklyScript = "scripts\manage_scheduler.py update --all"
Create-DataUpdateTask -TaskName "ProForma_WeeklyDataUpdate" -Schedule "Weekly" -StartTime "02:00" -ScriptArgs $WeeklyScript

# Monthly updates for real estate data (First Monday of month at 3:00 AM)
$MonthlyScript = "scripts\manage_scheduler.py update --all"
Create-DataUpdateTask -TaskName "ProForma_MonthlyDataUpdate" -Schedule "Monthly" -StartTime "03:00" -ScriptArgs $MonthlyScript

# Health check task (Daily at 1:00 AM)
$HealthCheckScript = "scripts\manage_scheduler.py freshness"
Create-DataUpdateTask -TaskName "ProForma_DataHealthCheck" -Schedule "Daily" -StartTime "01:00" -ScriptArgs $HealthCheckScript

Write-Host "`nScheduled tasks created successfully!" -ForegroundColor Green
Write-Host "`nTo manage tasks:" -ForegroundColor Cyan
Write-Host "- Open Task Scheduler (taskschd.msc)"
Write-Host "- Look for tasks starting with 'ProForma_'"
Write-Host "- You can modify schedules, enable/disable tasks, or run them manually"

Write-Host "`nTo test the setup:" -ForegroundColor Cyan
Write-Host "cd `"$ProjectPath`""
Write-Host "python scripts\manage_scheduler.py status"

Write-Host "`nSetup complete! Your data will now update automatically." -ForegroundColor Green