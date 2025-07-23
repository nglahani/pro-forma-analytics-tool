# Database Documentation

This document provides comprehensive documentation for the database architecture, schema design, and data management in the Pro-Forma Analytics Tool.

## 🗄️ Database Architecture

The application uses a multi-database SQLite architecture to separate concerns and optimize performance:

### Database Overview

| Database | Purpose | Size | Tables |
|----------|---------|------|--------|
| `market_data.db` | Market indicators and trends | ~168KB | 5+ tables |
| `economic_data.db` | Economic indicators and metrics | ~168KB | 4+ tables |
| `property_data.db` | Property-specific information | ~168KB | 6+ tables |
| `forecast_cache.db` | Cached forecasting data | ~168KB | 3+ tables |

### Database Relationships

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   market_data   │    │  economic_data  │    │  property_data  │
│                 │    │                 │    │                 │
│ • interest_rates│    │ • gdp_data      │    │ • properties    │
│ • market_trends │    │ • inflation     │    │ • units         │
│ • cap_rates     │    │ • employment    │    │ • leases        │
│ • vacancy_rates │    │ • demographics  │    │ • expenses      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ forecast_cache  │
                    │                 │
                    │ • predictions   │
                    │ • models        │
                    │ • scenarios     │
                    └─────────────────┘
```

## 📊 Schema Design

### Market Data Database (`market_data.db`)

#### Interest Rates Table
```sql
CREATE TABLE interest_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    rate_type VARCHAR(50) NOT NULL,
    rate_value DECIMAL(5,4) NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Market Trends Table
```sql
CREATE TABLE market_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    market_area VARCHAR(100) NOT NULL,
    trend_type VARCHAR(50) NOT NULL,
    trend_value DECIMAL(10,2) NOT NULL,
    units VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Cap Rates Table
```sql
CREATE TABLE cap_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    market_area VARCHAR(100) NOT NULL,
    cap_rate DECIMAL(5,4) NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Economic Data Database (`economic_data.db`)

#### GDP Data Table
```sql
CREATE TABLE gdp_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    gdp_value DECIMAL(15,2) NOT NULL,
    growth_rate DECIMAL(5,4),
    period_type VARCHAR(20) DEFAULT 'quarterly',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Inflation Data Table
```sql
CREATE TABLE inflation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    cpi_value DECIMAL(8,2) NOT NULL,
    inflation_rate DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Property Data Database (`property_data.db`)

#### Properties Table
```sql
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_name VARCHAR(200) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    property_type VARCHAR(50),
    total_units INTEGER,
    year_built INTEGER,
    acquisition_date DATE,
    acquisition_price DECIMAL(15,2),
    current_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Units Table
```sql
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    unit_number VARCHAR(20),
    unit_type VARCHAR(50),
    square_feet INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    rent_amount DECIMAL(10,2),
    occupied BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);
```

#### Leases Table
```sql
CREATE TABLE leases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    tenant_name VARCHAR(200),
    lease_start_date DATE,
    lease_end_date DATE,
    monthly_rent DECIMAL(10,2),
    security_deposit DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (unit_id) REFERENCES units(id)
);
```

### Forecast Cache Database (`forecast_cache.db`)

#### Predictions Table
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(100) NOT NULL,
    prediction_date DATE NOT NULL,
    target_date DATE NOT NULL,
    predicted_value DECIMAL(15,2) NOT NULL,
    confidence_interval_lower DECIMAL(15,2),
    confidence_interval_upper DECIMAL(15,2),
    model_parameters TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Database Management

### Database Manager

The `database_manager.py` provides centralized database operations:

```python
class DatabaseManager:
    def __init__(self):
        self.market_db = "data/databases/market_data.db"
        self.economic_db = "data/databases/economic_data.db"
        self.property_db = "data/databases/property_data.db"
        self.forecast_db = "data/databases/forecast_cache.db"
    
    def init_databases(self):
        """Initialize all databases with schema"""
        pass
    
    def backup_databases(self):
        """Create backup of all databases"""
        pass
    
    def restore_databases(self, backup_path):
        """Restore databases from backup"""
        pass
```

### Common Operations

#### Connecting to Databases
```python
import sqlite3

def get_connection(db_path):
    return sqlite3.connect(db_path)

# Usage
with get_connection('data/databases/market_data.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interest_rates LIMIT 10")
    results = cursor.fetchall()
```

#### Data Insertion
```python
def insert_market_data(db_path, data):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO market_trends (date, market_area, trend_type, trend_value)
            VALUES (?, ?, ?, ?)
        """, (data['date'], data['market_area'], data['trend_type'], data['trend_value']))
        conn.commit()
```

#### Data Retrieval
```python
def get_market_trends(db_path, market_area=None, start_date=None, end_date=None):
    query = "SELECT * FROM market_trends WHERE 1=1"
    params = []
    
    if market_area:
        query += " AND market_area = ?"
        params.append(market_area)
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
```

## 📈 Data Models

### Market Data Models

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

@dataclass
class InterestRate:
    id: Optional[int]
    date: date
    rate_type: str
    rate_value: Decimal
    source: Optional[str]
    created_at: Optional[date]
    updated_at: Optional[date]

@dataclass
class MarketTrend:
    id: Optional[int]
    date: date
    market_area: str
    trend_type: str
    trend_value: Decimal
    units: Optional[str]
    created_at: Optional[date]
```

### Property Data Models

```python
@dataclass
class Property:
    id: Optional[int]
    property_name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    property_type: Optional[str]
    total_units: Optional[int]
    year_built: Optional[int]
    acquisition_date: Optional[date]
    acquisition_price: Optional[Decimal]
    current_value: Optional[Decimal]
    created_at: Optional[date]
    updated_at: Optional[date]

@dataclass
class Unit:
    id: Optional[int]
    property_id: int
    unit_number: Optional[str]
    unit_type: Optional[str]
    square_feet: Optional[int]
    bedrooms: Optional[int]
    bathrooms: Optional[Decimal]
    rent_amount: Optional[Decimal]
    occupied: bool
```

## 🔄 Data Migration

### Migration Strategy

1. **Version Control**: Each migration is versioned
2. **Rollback Support**: All migrations are reversible
3. **Data Preservation**: Existing data is preserved during migrations
4. **Testing**: Migrations are tested before deployment

### Migration Example

```python
class Migration:
    def __init__(self, version, description):
        self.version = version
        self.description = description
    
    def up(self, connection):
        """Apply migration"""
        pass
    
    def down(self, connection):
        """Rollback migration"""
        pass

# Example migration
class AddPropertyTaxTable(Migration):
    def __init__(self):
        super().__init__(1, "Add property tax table")
    
    def up(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE property_taxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                tax_year INTEGER NOT NULL,
                tax_amount DECIMAL(10,2) NOT NULL,
                assessment_value DECIMAL(15,2),
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        """)
        connection.commit()
    
    def down(self, connection):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE property_taxes")
        connection.commit()
```

## 🔍 Data Validation

### Validation Rules

```python
def validate_property_data(property_data):
    errors = []
    
    # Required fields
    if not property_data.get('property_name'):
        errors.append("Property name is required")
    
    # Data type validation
    if property_data.get('total_units') and not isinstance(property_data['total_units'], int):
        errors.append("Total units must be an integer")
    
    # Range validation
    if property_data.get('year_built'):
        year = property_data['year_built']
        if year < 1800 or year > 2030:
            errors.append("Year built must be between 1800 and 2030")
    
    return errors
```

## 📊 Performance Optimization

### Indexing Strategy

```sql
-- Market data indexes
CREATE INDEX idx_interest_rates_date ON interest_rates(date);
CREATE INDEX idx_interest_rates_type ON interest_rates(rate_type);
CREATE INDEX idx_market_trends_area_date ON market_trends(market_area, date);

-- Property data indexes
CREATE INDEX idx_properties_city_state ON properties(city, state);
CREATE INDEX idx_units_property_id ON units(property_id);
CREATE INDEX idx_leases_unit_id ON leases(unit_id);

-- Economic data indexes
CREATE INDEX idx_gdp_data_date ON gdp_data(date);
CREATE INDEX idx_inflation_data_date ON inflation_data(date);
```

### Query Optimization

```python
def optimized_market_query(db_path, market_area, start_date, end_date):
    """Optimized query with proper indexing"""
    query = """
        SELECT date, trend_type, trend_value
        FROM market_trends 
        WHERE market_area = ? 
        AND date BETWEEN ? AND ?
        ORDER BY date DESC
    """
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA optimize")
        cursor = conn.cursor()
        cursor.execute(query, (market_area, start_date, end_date))
        return cursor.fetchall()
```

## 🔒 Data Security

### Access Control

```python
class DatabaseSecurity:
    def __init__(self):
        self.allowed_users = set()
        self.read_only_users = set()
    
    def check_permission(self, user_id, operation, table):
        """Check user permissions for database operations"""
        if operation == 'read':
            return user_id in self.allowed_users
        elif operation == 'write':
            return user_id in self.allowed_users and user_id not in self.read_only_users
        return False
```

### Data Encryption

```python
import hashlib
import os

def hash_sensitive_data(data):
    """Hash sensitive data before storage"""
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
    return salt + hashed

def verify_sensitive_data(data, hashed_data):
    """Verify sensitive data"""
    salt = hashed_data[:16]
    stored_hash = hashed_data[16:]
    computed_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
    return stored_hash == computed_hash
```

## 📈 Monitoring and Maintenance

### Database Health Checks

```python
def check_database_health():
    """Perform database health checks"""
    checks = {
        'market_data': check_market_data_integrity(),
        'economic_data': check_economic_data_integrity(),
        'property_data': check_property_data_integrity(),
        'forecast_cache': check_forecast_cache_integrity()
    }
    return checks

def check_market_data_integrity():
    """Check market data database integrity"""
    with sqlite3.connect('data/databases/market_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        return cursor.fetchone()[0] == 'ok'
```

### Backup Strategy

```python
import shutil
from datetime import datetime

def backup_databases():
    """Create timestamped backup of all databases"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    databases = [
        'data/databases/market_data.db',
        'data/databases/economic_data.db',
        'data/databases/property_data.db',
        'data/databases/forecast_cache.db'
    ]
    
    for db in databases:
        if os.path.exists(db):
            backup_path = f"{backup_dir}/{os.path.basename(db)}"
            shutil.copy2(db, backup_path)
    
    return backup_dir
```

## 🚨 Troubleshooting

### Common Database Issues

1. **Locked Database**
   ```bash
   # Check for locks
   ls -la data/databases/*.db-wal
   ls -la data/databases/*.db-shm
   
   # Remove locks (if safe)
   rm data/databases/*.db-wal
   rm data/databases/*.db-shm
   ```

2. **Corrupted Database**
   ```bash
   # Check integrity
   sqlite3 data/databases/market_data.db "PRAGMA integrity_check"
   
   # Recover from backup
   cp backups/latest/market_data.db data/databases/
   ```

3. **Performance Issues**
   ```bash
   # Analyze query performance
   sqlite3 data/databases/market_data.db "EXPLAIN QUERY PLAN SELECT * FROM market_trends"
   
   # Optimize database
   sqlite3 data/databases/market_data.db "PRAGMA optimize"
   ```

## 📚 Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite Performance](https://www.sqlite.org/optoverview.html)
- [Database Design Best Practices](https://www.sqlite.org/foreignkeys.html)