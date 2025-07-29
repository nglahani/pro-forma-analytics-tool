"""
Windows Task Scheduler Setup

Sets up automated Windows Task Scheduler jobs for data collection.
This script creates scheduled tasks to run the data scheduler at configured intervals.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime, time
import json


def create_task_xml(task_name: str, python_path: str, script_path: str, 
                   start_time: str = "02:00", frequency: str = "WEEKLY") -> str:
    """Create Windows Task Scheduler XML configuration."""
    
    # Convert time to proper format
    start_datetime = datetime.combine(datetime.today(), time.fromisoformat(start_time))
    start_time_formatted = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    
    xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}</Date>
    <Author>Pro Forma Analytics Tool</Author>
    <Description>Automated market data collection for real estate analytics</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{start_time_formatted}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Sunday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>P1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}" update --all</Arguments>
      <WorkingDirectory>{Path(script_path).parent.parent}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    return xml_template


def setup_windows_tasks():
    """Set up Windows Task Scheduler tasks for data collection."""
    
    print("Setting up Windows Task Scheduler for automated data collection...")
    
    # Get current Python executable and script paths
    python_path = sys.executable
    project_root = Path(__file__).parent.parent
    manage_scheduler_path = project_root / "scripts" / "manage_scheduler.py"
    
    print(f"Python executable: {python_path}")
    print(f"Scheduler script: {manage_scheduler_path}")
    print(f"Working directory: {project_root}")
    
    # Load current schedule configuration to get frequencies
    schedule_config_path = project_root / "data" / "scheduler" / "schedule_config.json"
    
    if not schedule_config_path.exists():
        print("ERROR: Schedule configuration not found. Please run the scheduler first.")
        return False
    
    try:
        with open(schedule_config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load schedule configuration: {e}")
        return False
    
    # Create tasks for different frequencies
    frequency_groups = {
        'weekly': [],
        'monthly': [],
        'quarterly': []
    }
    
    # Group parameters by frequency
    for param_name, param_config in config.get('scheduled_updates', {}).items():
        frequency = param_config.get('frequency', 'monthly')
        if frequency in frequency_groups:
            frequency_groups[frequency].append(param_name)
    
    # Create scheduled tasks
    tasks_created = 0
    
    for frequency, parameters in frequency_groups.items():
        if not parameters:
            continue
            
        task_name = f"ProFormaAnalytics_{frequency.title()}Update"
        
        print(f"\nCreating task: {task_name}")
        print(f"  Frequency: {frequency}")
        print(f"  Parameters: {', '.join(parameters)}")
        
        # Create XML configuration
        xml_content = create_task_xml(
            task_name=task_name,
            python_path=python_path,
            script_path=str(manage_scheduler_path),
            start_time="02:00",
            frequency=frequency.upper()
        )
        
        # Save XML to temporary file
        xml_file = project_root / f"{task_name}.xml"
        try:
            with open(xml_file, 'w', encoding='utf-16') as f:
                f.write(xml_content)
            
            # Create the scheduled task
            cmd = [
                'schtasks', '/create', 
                '/tn', task_name,
                '/xml', str(xml_file),
                '/f'  # Force creation (overwrite if exists)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"  ✓ Successfully created task: {task_name}")
                tasks_created += 1
            else:
                print(f"  ✗ Failed to create task: {task_name}")
                print(f"    Error: {result.stderr}")
            
            # Clean up XML file
            xml_file.unlink()
            
        except Exception as e:
            print(f"  ✗ Error creating task {task_name}: {e}")
            if xml_file.exists():
                xml_file.unlink()
    
    if tasks_created > 0:
        print(f"\n✓ Successfully created {tasks_created} scheduled tasks")
        print("\nTo view your scheduled tasks:")
        print("  schtasks /query /tn ProFormaAnalytics*")
        print("\nTo run a task manually:")
        print("  schtasks /run /tn ProFormaAnalytics_WeeklyUpdate")
        return True
    else:
        print("\n✗ No tasks were created successfully")
        return False


def list_existing_tasks():
    """List existing Pro Forma Analytics scheduled tasks."""
    
    print("Existing Pro Forma Analytics scheduled tasks:\n")
    
    cmd = ['schtasks', '/query', '/fo', 'table', '/tn', 'ProFormaAnalytics*']
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("No Pro Forma Analytics tasks found or error occurred:")
        print(result.stderr)


def remove_existing_tasks():
    """Remove existing Pro Forma Analytics scheduled tasks."""
    
    print("Removing existing Pro Forma Analytics scheduled tasks...")
    
    task_names = [
        'ProFormaAnalytics_WeeklyUpdate',
        'ProFormaAnalytics_MonthlyUpdate', 
        'ProFormaAnalytics_QuarterlyUpdate'
    ]
    
    for task_name in task_names:
        cmd = ['schtasks', '/delete', '/tn', task_name, '/f']
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"  ✓ Removed task: {task_name}")
        else:
            # Task might not exist, which is fine
            pass


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Windows Task Scheduler for Pro Forma Analytics")
    parser.add_argument('action', choices=['setup', 'list', 'remove'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        # Remove existing tasks first
        remove_existing_tasks()
        # Setup new tasks
        success = setup_windows_tasks()
        if success:
            print("\n" + "="*60)
            print("WINDOWS TASK SCHEDULER SETUP COMPLETE")
            print("="*60)
            print("Your market data will now be updated automatically:")
            print("  • Weekly: Interest rates (Sunday 2:00 AM)")
            print("  • Monthly: Property data (Sunday 2:00 AM)")  
            print("  • Quarterly: Lending data (Sunday 2:00 AM)")
            print("\nMonitor task execution in Windows Task Scheduler or check logs.")
        else:
            sys.exit(1)
            
    elif args.action == 'list':
        list_existing_tasks()
        
    elif args.action == 'remove':
        remove_existing_tasks()
        print("All Pro Forma Analytics scheduled tasks removed.")