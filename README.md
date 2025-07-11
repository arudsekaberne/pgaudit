# AWS EC2 PostgreSQL with pgAudit Setup Guide

This guide walks you through creating an AWS EC2 instance with PostgreSQL and the pgAudit extension for database auditing.

## Prerequisites

- AWS Account with appropriate permissions
- SSH client (Terminal, PuTTY, etc.)
- Database client (DBeaver, pgAdmin, etc.) for testing

## Step 1: Create AWS EC2 Instance

### 1.1 Launch EC2 Instance
1. Log into AWS Console and navigate to EC2 Dashboard
2. Click "Launch Instance"
3. Configure the following settings:
   - **Name**: Give your instance a descriptive name (e.g., "PostgreSQL-Server")
   - **AMI**: Select Ubuntu Server (latest LTS version recommended)
   - **Key Pair**: Create a new key pair
     - Key pair name: `postgre-poc-keypair` (or your preferred name)
     - Key pair type: RSA
     - Private key file format: .pem

### 1.2 Configure Security Group
1. Create a new security group or modify the default
2. Add the following inbound rules:
   - **PostgreSQL**: Port 5432, Source: Anywhere-IPv4 (for external access)

### 1.3 Allocate Elastic IP
1. After instance launch, go to EC2 Dashboard → Elastic IPs
2. Select the allocated IP → Actions → Associate Elastic IP address
3. Choose your EC2 instance and associate

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
# For PostgreSQL 16 (adjust version number as needed)
apt search postgresql-16-pgaudit
sudo apt install -y postgresql-16-pgaudit
```

### 6.2 Verify pgAudit Availability
```bash
sudo -u postgres psql -c "SELECT * FROM pg_available_extensions WHERE name = 'pgaudit';"
```

### 6.3 Create pgAudit Extension
```bash
sudo -u postgres psql -c "CREATE EXTENSION pgaudit;"
```

### 6.4 Verify Extension Installation
```bash
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

### 8.1 Basic pgAudit Configuration
```bash
sudo vi /etc/postgresql/16/main/postgresql.conf
```

### 8.2 Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

### 8.3 Verify pgAudit Settings
```bash
sudo -u postgres psql -c "SHOW pgaudit.log;"
```

## Conclusion

You now have a fully configured AWS EC2 instance running PostgreSQL with pgAudit extension. The database is accessible remotely and ready for auditing database activities. Remember to follow security best practices and regularly monitor your setup.
