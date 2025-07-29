# Live Data Input Infrastructure Setup Guide

This guide covers the complete setup and management of the automated data update system for keeping your pro forma market data fresh and current.

## Overview

The live data input infrastructure provides:
- **Automated data collection** from multiple sources
- **Configurable update schedules** (daily, weekly, monthly, quarterly)
- **Data freshness monitoring** with staleness alerts
- **Cross-platform scheduling** (Windows Task Scheduler, cron, systemd)
- **Error handling and retry logic**
- **Quality validation** and outlier detection

## Quick Start

### 1. Data Replacement (One-Time Setup)

First, replace all mock data with real market data:

```bash
# Navigate to project directory
cd /path/to/pro-forma-analytics-tool

# Replace mock data (this may take a few minutes)
python scripts/replace_mock_data.py
```

**Expected Output:**
```
Total jobs executed: 40
Successful jobs: 30+
Success rate: 75.0%+
Total records collected: 480+
```

### 2. Check Data Status

Verify the data replacement was successful:

```bash
python scripts/manage_scheduler.py status
```

### 3. Check Data Freshness

See which data needs updates:

```bash
python scripts/manage_scheduler.py freshness
```

### 4. Test Immediate Update

Test updating a single parameter:

```bash
python scripts/manage_scheduler.py update cap_rate
```

## Automated Scheduling Setup

Choose your platform and follow the appropriate setup:

### Windows (Task Scheduler)

**Option 1: PowerShell Script (Recommended)**
```powershell
# Run as Administrator
# Update the paths in the script first
.\scripts\setup_windows_scheduler.ps1 -ProjectPath "C:\your\project\path" -FredApiKey "your_api_key"
```

**Option 2: Manual Task Scheduler Setup**
1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Set trigger (weekly/monthly)
4. Set action: `python scripts/manage_scheduler.py update --all`
5. Configure to run whether user is logged on or not

### Linux/macOS (Cron)

**Option 1: Setup Script**
```bash
# Edit paths in the script first
chmod +x scripts/cron_setup.sh
./scripts/cron_setup.sh
```

**Option 2: Manual Cron Setup**
```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths):
# Weekly updates (Mondays at 2 AM)
0 2 * * 1 cd /path/to/project && python3 scripts/manage_scheduler.py update --all

# Daily health check (1 AM)
0 1 * * * cd /path/to/project && python3 scripts/manage_scheduler.py freshness
```

### Linux (Systemd Service)

```bash
# 1. Copy and edit the service file
sudo cp scripts/proforma-data-updater.service /etc/systemd/system/
sudo nano /etc/systemd/system/proforma-data-updater.service

# 2. Update paths and API key in the file

# 3. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable proforma-data-updater.service
sudo systemctl start proforma-data-updater.service

# 4. Check status
sudo systemctl status proforma-data-updater.service
```

## Configuration Management

### View Current Schedule

```bash
python scripts/manage_scheduler.py config list
```

### Add Custom Schedule

```bash
# Add a parameter with custom schedule
python scripts/manage_scheduler.py config add treasury_10y --frequency weekly --time 08:00 --geo-codes NATIONAL
```

### Enable/Disable Updates

```bash
# Disable a parameter update
python scripts/manage_scheduler.py config disable property_growth

# Enable it back
python scripts/manage_scheduler.py config enable property_growth
```

### Remove Schedule

```bash
python scripts/manage_scheduler.py config remove old_parameter
```

## Update Frequencies by Parameter Type

| Parameter Category | Default Frequency | Rationale |
|-------------------|------------------|-----------|
| **Interest Rates** | Weekly | High volatility, market-sensitive |
| **Real Estate Metrics** | Monthly | Moderate changes, survey-based |
| **Lending Requirements** | Quarterly | Stable, regulatory-driven |

### Interest Rates (Weekly Updates)
- `treasury_10y` - 10-Year Treasury Rate
- `fed_funds_rate` - Federal Funds Rate
- `commercial_mortgage_rate` - Commercial Mortgage Rate

### Real Estate Market (Monthly Updates)
- `cap_rate` - Multifamily Cap Rates by MSA
- `vacancy_rate` - Rental Vacancy Rates
- `rent_growth` - Annual Rent Growth
- `property_growth` - Property Value Growth
- `expense_growth` - Operating Expense Growth

### Lending Requirements (Quarterly Updates)
- `ltv_ratio` - Loan-to-Value Ratios
- `closing_cost_pct` - Closing Cost Percentages
- `lender_reserves` - Lender Reserve Requirements

## Manual Data Updates

### Update All Parameters

```bash
python scripts/manage_scheduler.py update --all
```

### Update Specific Parameter

```bash
python scripts/manage_scheduler.py update cap_rate
```

### Update by Geography

The system automatically handles geographic scope:
- **National parameters**: Interest rates (FRED data)
- **MSA-specific parameters**: Real estate and lending data for 5 major MSAs

## Data Sources

### Current Data Sources

| Source Type | Parameters | Geographic Scope | Update Method |
|-------------|------------|------------------|---------------|
| **FRED API** | Interest rates, economic indicators | National | API calls |
| **Market Research** | Cap rates, vacancy, rent growth | 5 MSAs | Economic modeling |
| **Industry Surveys** | Lending requirements | 5 MSAs | Market analysis |

### Supported Geographic Markets

- **16980**: Chicago-Naperville-Elgin, IL-IN-WI
- **31080**: Los Angeles-Long Beach-Anaheim, CA
- **33100**: Miami-Fort Lauderdale-West Palm Beach, FL
- **35620**: New York-Newark-Jersey City, NY-NJ-PA
- **47900**: Washington-Arlington-Alexandria, DC-VA-MD-WV

## Monitoring and Maintenance

### Data Freshness Monitoring

The system automatically monitors data age and flags stale data:

```bash
# Check data freshness
python scripts/manage_scheduler.py freshness
```

**Staleness Thresholds:**
- Daily updates: 3 days
- Weekly updates: 10 days
- Monthly updates: 40 days
- Quarterly updates: 100 days

### Health Checks

The scheduler runs automatic health checks:
- **Daily at 1:00 AM**: Data freshness check
- **Logs stale parameters** for attention
- **Recommends actions** for urgent updates

### Error Handling

The system includes comprehensive error handling:
- **Retry logic** for temporary failures
- **Quality validation** with outlier detection
- **Graceful degradation** when sources are unavailable
- **Detailed logging** for troubleshooting

## Troubleshooting

### Common Issues

**1. "FRED API key not found"**
```bash
# Set environment variable
export FRED_API_KEY="your_api_key_here"

# Or set in Windows
set FRED_API_KEY=your_api_key_here
```

**2. "No module named 'schedule'"**
```bash
pip install schedule
```

**3. "Data quality issues - High outlier rate"**
This is normal for market-modeled data. The system still saves the data but logs a warning for review.

**4. Permission errors on Linux**
```bash
# Ensure proper ownership
chown -R $USER:$USER /path/to/project

# Or run with sudo for system-wide setup
sudo python scripts/manage_scheduler.py update --all
```

### Log Files

Check logs for detailed error information:
- **Windows**: Event Viewer or console output
- **Linux**: `journalctl -u proforma-data-updater` (if using systemd)
- **Cron logs**: `/var/log/cron` or `grep CRON /var/log/syslog`

## API Key Setup

### FRED API Key (Recommended)

1. **Get API Key**: Visit [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
2. **Register** for free account
3. **Set Environment Variable**:
   ```bash
   # Linux/macOS
   echo "export FRED_API_KEY=your_key_here" >> ~/.bashrc
   source ~/.bashrc
   
   # Windows
   setx FRED_API_KEY "your_key_here"
   ```

### Future API Integrations

The system is designed to easily add new data sources:
- **RentSpree API** for rental market data
- **CoStar API** for commercial real estate
- **Bloomberg API** for financial markets
- **Census Bureau APIs** for demographic data

## Performance Optimization

### Database Optimization

The system uses SQLite with optimizations:
- **Indexed tables** for fast queries
- **Batch inserts** for efficiency
- **Automatic backup** before major updates
- **Connection pooling** for concurrent access

### Update Optimization

- **Incremental updates**: Only collect recent data (last 2 years)
- **Parallel processing**: Multiple collectors run simultaneously
- **Quality validation**: Skip duplicate data
- **Smart scheduling**: Different frequencies by parameter type

## Advanced Configuration

### Custom Update Frequencies

Edit `data/scheduler/schedule_config.json`:

```json
{
  "scheduled_updates": {
    "custom_parameter": {
      "geographic_codes": ["35620"],
      "frequency": "weekly",
      "time_of_day": "03:00",
      "enabled": true
    }
  }
}
```

### Quality Thresholds

Modify quality validation in collectors:
- **Outlier detection**: Adjust `expected_range` parameters
- **Completeness**: Set minimum data point requirements
- **Freshness**: Customize staleness thresholds

### Custom Data Sources

Add new collectors by extending `BaseDataCollector`:

```python
from data.collectors.base_collector import BaseDataCollector

class CustomDataCollector(BaseDataCollector):
    def collect_data(self, parameter_name, geographic_code, start_date, end_date):
        # Your custom data collection logic
        pass
```

## Production Deployment

### High Availability Setup

For production environments:

1. **Database Replication**: Consider PostgreSQL for high-volume usage
2. **Load Balancing**: Distribute collection jobs across multiple workers
3. **Monitoring**: Integrate with APM tools (DataDog, New Relic)
4. **Alerting**: Set up notifications for failed updates
5. **Backup Strategy**: Regular database backups with retention policy

### Security Considerations

- **API Key Management**: Use secrets manager (AWS Secrets, Azure Key Vault)
- **Network Security**: Firewall rules for API access
- **Access Control**: Limit permissions for scheduler service account
- **Audit Logging**: Track all data updates and access

## Support and Maintenance

### Regular Maintenance Tasks

- **Weekly**: Review data freshness report
- **Monthly**: Check error rates and update success metrics
- **Quarterly**: Review and update data source configurations
- **Annually**: Evaluate new data sources and geographic expansion

### Backup and Recovery

The system automatically creates backups before major updates:
- **Location**: `data/databases/*_backup_YYYYMMDD_HHMMSS.db`
- **Retention**: Manual cleanup recommended
- **Recovery**: Replace current database with backup file

---

## Summary

The live data input infrastructure provides a robust, automated system for keeping your pro forma market data current. Key benefits:

✅ **Automated Updates**: Set-and-forget scheduling  
✅ **Quality Monitoring**: Automatic validation and alerts  
✅ **Cross-Platform**: Works on Windows, Linux, macOS  
✅ **Scalable**: Easy to add new parameters and data sources  
✅ **Production-Ready**: Error handling, logging, backup/recovery  

Your market data will now stay fresh automatically, providing more accurate DCF analysis results.