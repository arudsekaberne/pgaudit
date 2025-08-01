# AWS EC2 PostgreSQL with pgAudit Setup Guide

This guide walks you through creating an AWS EC2 instance with PostgreSQL and the pgAudit extension for database auditing.

## Prerequisites

- AWS Account
- SSH client (Terminal, PuTTY, etc.)
- Database client (DBeaver, pgAdmin, etc.) for testing

## Step 1: Create AWS EC2 Instance
1. Launch EC2 Instance with Ubuntu Server (default configuration)
2. Create a new .pem key pair during instance creation
3. Add inbound rule: PostgreSQL (Port 5432, Source: Anywhere-IPv4)
4. Allocate a dedicated Elastic IP address

## Step 2: Connect to EC2 Instance
```bash
ssh -i "/path/to/your/keypair.pem" ubuntu@your-elastic-ip-address
```

## Step 3: Install PostgreSQL

```bash
# Update System Packages
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Verify Installation
sudo systemctl status postgresql
```

## Step 4: Configure PostgreSQL

```bash
# Access PostgreSQL
sudo -u postgres psql

# Set Password for postgres User
ALTER USER postgres WITH PASSWORD 'postgres123';

# Check PostgreSQL Version
SELECT version();

# Exit PostgreSQL
\q
```

## Step 5: Configure Remote Access

### 5.1 Modify PostgreSQL Configuration
```bash
# Find config file location
sudo -u postgres psql -c "SHOW config_file;"

# Edit postgresql.conf (adjust path based on your PostgreSQL version)
sudo vi /etc/postgresql/16/main/postgresql.conf
```

**Add/modify the following line:**
```
listen_addresses = '*'
```

### 5.2 Configure Host-Based Authentication
```bash
# Find HBA file location
sudo -u postgres psql -c "SHOW hba_file;"

# Edit pg_hba.conf
sudo vi /etc/postgresql/16/main/pg_hba.conf
```

**Add the following line at the end:**
```
host    all             all            0.0.0.0/0        md5
```

### 5.3 Restart PostgreSQL
```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

## Step 6: Install pgAudit Extension

### 6.1 Search and Install pgAudit Package
```bash

# Search for selective pgAudit Package (adjust version number as needed)
apt search postgresql-16-pgaudit

# Install selective pgAudit Package
sudo apt install -y postgresql-16-pgaudit

# Verify pgAudit Availability
sudo -u postgres psql -c "SELECT * FROM pg_available_extensions WHERE name = 'pgaudit';"

# Create pgAudit Extension
sudo -u postgres psql -c "CREATE EXTENSION pgaudit;"

# Verify Extension Installation
sudo -u postgres psql -c "SELECT * FROM pg_extension WHERE extname = 'pgaudit';"
```

## Step 7: Test Connection

### 7.1 Test Local Connection
```bash
psql -h localhost -U postgres -d postgres
```

### 7.2 Test Remote Connection
Use a database client like DBeaver with the following connection details:
- **Host**: Your Elastic IP address
- **Port**: 5432
- **Database**: postgres
- **Username**: postgres
- **Password**: postgres123

## Step 8: Configure pgAudit (Optional)
 
```bash
# Basic pgAudit Configuration
sudo vi /etc/postgresql/16/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify pgAudit Settings
sudo -u postgres psql -c "SHOW pgaudit.log;"
```

## Conclusion

You now have a fully configured AWS EC2 instance running PostgreSQL with pgAudit extension. The database is accessible remotely and ready for auditing database activities. Remember to follow security best practices and regularly monitor your setup.

## References

### Official Documentation
- [PgAudit Official Documentation](https://github.com/pgaudit/pgaudit?tab=readme-ov-file#pgaudit--open-source-postgresql-audit-logging)
- [PostgreSQL Native Logging Official Documentation](https://www.postgresql.org/docs/current/runtime-config-logging.html#RUNTIME-CONFIG-LOGGING)
- [PostgreSQL Log Schema](https://www.postgresql.org/docs/current/runtime-config-logging.html#RUNTIME-CONFIG-LOGGING-JSONLOG)
- [PgAudit Log Format](https://github.com/pgaudit/pgaudit?tab=readme-ov-file#format)
  
### Video Tutorials
- [PostgreSQL on Amazon EC2 Instance](https://www.youtube.com/watch?v=iHX-jtKIVNA)
- [Assign Elastic IP to AWS EC2 instance](https://www.youtube.com/watch?v=d3s385C0QCw&lc=UgwWvj2U40y3l_DYGnB4AaABAg)
