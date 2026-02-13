# DML Marketing Middleware

Production-grade API middleware for Direct Mortgage Loans (DML) to receive webform lead submissions, normalize data, and sync to Total Expert CRM.

## Architecture Overview

```
Formidable Webforms 
    ↓ (POST /api/v1/leads/webform)
Azure Web App (Django REST API)
    ↓ (stores to)
Azure MySQL Database
    ↓ (queues to)
Azure Service Bus
    ↓ (processed by worker)
Total Expert CRM
```

## Features

- ✅ REST API endpoint for Formidable webform submissions
- ✅ MySQL database for persistent storage
- ✅ Azure Service Bus integration for async processing
- ✅ Loan Officer management by slug
- ✅ Lead submission tracking with status workflow
- ✅ Django admin interface for data management
- ✅ Comprehensive logging
- ✅ Health check endpoint

## Tech Stack

- **Framework**: Django 5.0.12
- **Database**: Azure MySQL
- **Message Queue**: Azure Service Bus
- **Web Server**: Gunicorn
- **Platform**: Azure App Service (Linux, Python 3.11)
- **CRM Integration**: Total Expert API

## Project Structure

```
dml-marketing-middleware/
├── config/                 # Django project configuration
│   ├── settings.py        # Settings with MySQL & Azure config
│   ├── urls.py            # Main URL routing
│   ├── wsgi.py            # WSGI entry point
│   └── asgi.py            # ASGI entry point
├── core/                  # Core app (Loan Officers)
│   ├── models.py          # LoanOfficer model
│   └── admin.py           # Admin configuration
├── leads/                 # Leads app (Submissions)
│   ├── models.py          # LeadSubmission model
│   ├── views.py           # API endpoints
│   ├── admin.py           # Admin configuration
│   ├── servicebus.py      # Service Bus integration
│   └── urls.py            # URL routing
├── manage.py              # Django management script
├── startup.sh             # Azure startup script
└── requirements.txt       # Python dependencies
```

## Database Schema

### loan_officers
- `id` (UUID, PK)
- `slug` (VARCHAR 120, UNIQUE) - URL path component
- `first_name`, `last_name`, `email`, `phone`
- `te_owner_id` - Total Expert user ID
- `is_active` - Whether LO accepts leads
- `created_at`, `updated_at`

### lead_submissions
- `id` (UUID, PK)
- `loan_officer_id` (FK → loan_officers)
- `source` - Lead source (e.g., "webform")
- `submitted_at` - Timestamp
- `page_url`, `referrer`, `ip_address`, `user_agent` - Request metadata
- `first_name`, `last_name`, `email`, `phone` - Lead data
- `raw_payload` (JSON) - Complete form submission
- `status` - Workflow status (received/queued/synced/failed)
- `te_contact_id` - Total Expert contact ID after sync
- `attempt_count`, `last_error` - Retry tracking
- `queued_at`, `synced_at` - Processing timestamps

## API Endpoints

### POST /api/v1/leads/webform
Receive lead submissions from Formidable webforms.

**Request Body:**
```json
{
  "lo_slug": "john-smith",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "phone": "555-1234",
  "page_url": "https://directmortgageloans.com/john-smith",
  "referrer": "https://google.com"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "id": "a1b2c3d4-...",
  "status": "queued",
  "message": "Lead received and queued for processing"
}
```

### GET /health
Health check endpoint for Azure monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "dml-marketing-middleware"
}
```

## Azure Setup Guide

### 1. Create Azure MySQL Database

```bash
# In Azure Portal:
# - Create Azure Database for MySQL (Flexible Server)
# - Server name: dml-mysql-server
# - Database name: dml_marketing_middleware
# - Admin username: dmladmin
# - Admin password: [secure password]
# - Region: East US 2
# - Compute tier: Burstable (B1ms recommended for dev)
# - Enable SSL enforcement
```

### 2. Configure Azure Web App

In Azure Portal → App Service → middleware-api → Configuration:

**Application Settings:**
```
DJANGO_SECRET_KEY=<generate-with-python-secrets>
DJANGO_DEBUG=0
AZURE_ALLOW_ALL_HOSTS=1

MYSQL_HOST=dml-mysql-server.mysql.database.azure.com
MYSQL_PORT=3306
MYSQL_DATABASE=dml_marketing_middleware
MYSQL_USER=dmladmin
MYSQL_PASSWORD=<your-mysql-password>
MYSQL_SSL=1

SERVICEBUS_CONNECTION_STRING=<from-service-bus-shared-access-policy>
SERVICEBUS_QUEUE_NAME=webform-leads

TOTAL_EXPERT_CLIENT_ID=<from-total-expert>
TOTAL_EXPERT_CLIENT_SECRET=<from-total-expert>
TOTAL_EXPERT_API_URL=https://api.totalexpert.net

DJANGO_CREATE_SUPERUSER=1
DJANGO_SUPERUSER_USERNAME=marketingadmin
DJANGO_SUPERUSER_EMAIL=jwalker@directmortgageloans.com
DJANGO_SUPERUSER_PASSWORD=<secure-password>
```

**General Settings:**
- Stack: Python 3.11
- Startup Command: `bash /home/site/wwwroot/startup.sh`

### 3. Deploy from GitHub

1. **Connect GitHub Repository:**
   - Azure Portal → Deployment Center
   - Source: GitHub
   - Organization: jadonwalker0
   - Repository: dml-marketing-middleware
   - Branch: main

2. **GitHub Actions Workflow** (auto-created by Azure):
   - Builds on push to main
   - Deploys to Azure Web App
   - Runs startup.sh which migrates database

### 4. Verify Deployment

```bash
# Check health endpoint
curl https://middleware-api-fagee5h3hzbtftca.eastus2-01.azurewebsites.net/health

# Check logs
az webapp log tail --name middleware-api --resource-group dml-marketing-middleware

# Access Django admin
https://middleware-api-fagee5h3hzbtftca.eastus2-01.azurewebsites.net/admin
```

## Local Development

### Prerequisites
- Python 3.11
- MySQL 8.0+ (or use Azure MySQL)
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/jadonwalker0/dml-marketing-middleware.git
cd dml-marketing-middleware

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local MySQL credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Testing the API

```bash
# Test webform endpoint
curl -X POST http://localhost:8000/api/v1/leads/webform \
  -H "Content-Type: application/json" \
  -d '{
    "lo_slug": "john-smith",
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "555-1234"
  }'
```

## Managing Loan Officers

### Via Django Admin
1. Go to `https://[your-domain]/admin`
2. Login with superuser credentials
3. Navigate to "Loan Officers"
4. Add/Edit loan officers with their slug and Total Expert owner ID

### Via Django Shell
```python
python manage.py shell

from core.models import LoanOfficer

# Create a loan officer
lo = LoanOfficer.objects.create(
    slug="john-smith",
    first_name="John",
    last_name="Smith",
    email="john.smith@directmortgageloans.com",
    phone="555-1234",
    te_owner_id="TE_USER_123",
    is_active=True
)

# List all active loan officers
LoanOfficer.objects.filter(is_active=True)
```

## Workflow

1. **Lead Submitted** → Formidable webform POSTs to `/api/v1/leads/webform`
2. **Validation** → API validates `lo_slug` and finds matching LoanOfficer
3. **Storage** → Lead saved to MySQL with status=RECEIVED
4. **Queueing** → Lead queued to Azure Service Bus (status→QUEUED)
5. **Processing** → Service Bus worker picks up message (future implementation)
6. **CRM Sync** → Worker syncs lead to Total Expert (status→SYNCED)
7. **Completion** → Lead marked with `te_contact_id` and `synced_at`

## Monitoring & Logs

```bash
# Stream logs in real-time
az webapp log tail --name middleware-api --resource-group dml-marketing-middleware

# Download log files
az webapp log download --name middleware-api --resource-group dml-marketing-middleware

# Check metrics in Azure Portal
# - Resource Group → middleware-api → Monitoring → Metrics
# - Track: HTTP requests, response time, errors
```

## Troubleshooting

### Database Connection Issues
```bash
# Test MySQL connection from Azure Web App console
mysql -h dml-mysql-server.mysql.database.azure.com -u dmladmin -p

# Check firewall rules - ensure Azure services have access
# Azure Portal → MySQL → Connection security → Allow Azure services
```

### Service Bus Issues
```bash
# Verify queue exists
az servicebus queue show \
  --resource-group dml-marketing-middleware \
  --namespace-name middleware-service-bus \
  --name webform-leads

# Check messages in queue
# Azure Portal → Service Bus → Queues → webform-leads → Service Bus Explorer
```

## Next Steps / Roadmap

- [ ] Implement Service Bus worker for async CRM sync
- [ ] Add Total Expert API integration
- [ ] Set up automated retries for failed syncs
- [ ] Add analytics dashboard
- [ ] Implement lead deduplication logic
- [ ] Add Slack/email notifications for errors
- [ ] Create management commands for bulk operations
- [ ] Add API authentication for security

## Support

For issues or questions:
- **Developer**: Jadon Walker (jwalker@directmortgageloans.com)
- **GitHub**: https://github.com/jadonwalker0/dml-marketing-middleware

## License

Proprietary - Direct Mortgage Loans
