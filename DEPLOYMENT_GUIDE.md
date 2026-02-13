# Deployment Guide: DML Marketing Middleware

## Fresh Start Deployment (Step-by-Step)

This guide will walk you through deploying the completely rebuilt middleware from scratch.

---

## Phase 1: Clean Up Azure (5 minutes)

### 1. Delete Old Web App
```
1. Go to Azure Portal: https://portal.azure.com
2. Navigate to: Resource Groups → dml-marketing-middleware
3. Find: middleware-api (Web App)
4. Click: Delete
5. Confirm: Type "middleware-api" and delete
```

**Keep These (DO NOT DELETE):**
- ✅ Resource Group: `dml-marketing-middleware`
- ✅ Service Bus: `middleware-service-bus`
- ✅ Service Bus Queue: `webform-leads`

---

## Phase 2: Set Up MySQL Database (15 minutes)

### 1. Create Azure MySQL Flexible Server

```
Azure Portal → Create Resource → Azure Database for MySQL Flexible Server

Basic Settings:
- Subscription: Azure CSP Subscription
- Resource Group: dml-marketing-middleware
- Server name: dml-mysql-server (or choose your own)
- Region: East US 2
- MySQL version: 8.0
- Workload type: Development

Compute + Storage:
- Compute tier: Burstable
- Compute size: B1ms (1 vCore, 2 GiB RAM)
- Storage: 20 GiB (default)
- Backup retention: 7 days

Authentication:
- Admin username: dmladmin
- Admin password: [CREATE SECURE PASSWORD - SAVE THIS]

Networking:
- Connectivity method: Public access
- Firewall rules:
  ✅ Add "AllowAzureServices" with 0.0.0.0 to 0.0.0.0
  ✅ Add your IP for management access

Click: Review + Create → Create
```

**Wait for deployment to complete (5-10 minutes)**

### 2. Create Database

```
1. After MySQL server deploys, click "Go to resource"
2. Left sidebar → Databases
3. Click: + Add
4. Database name: dml_marketing_middleware
5. Click: Save
```

### 3. Get Connection String

```
1. MySQL server → Connect (left sidebar)
2. Copy connection details:
   - Server name: dml-mysql-server.mysql.database.azure.com
   - Port: 3306
   - Admin username: dmladmin
   - Database: dml_marketing_middleware
```

**Save these for later!**

---

## Phase 3: Create New Web App (10 minutes)

### 1. Create App Service

```
Azure Portal → Create Resource → Web App

Basic:
- Subscription: Azure CSP Subscription
- Resource Group: dml-marketing-middleware
- Name: middleware-api-v2 (or keep middleware-api if deleted)
- Publish: Code
- Runtime stack: Python 3.11
- Operating System: Linux
- Region: East US 2

App Service Plan:
- Linux Plan: Create new "ASP-dmlmarketing-9c6b" or use existing
- Pricing plan: Basic B1 (or your preferred tier)

Click: Review + Create → Create
```

### 2. Configure Deployment Source

```
1. Go to new Web App → Deployment Center (left sidebar)
2. Source: GitHub
3. Authorize GitHub if prompted
4. Organization: jadonwalker0
5. Repository: dml-marketing-middleware
6. Branch: main
7. Click: Save

This creates the GitHub Actions workflow automatically.
```

---

## Phase 4: Configure Environment Variables (10 minutes)

### 1. Generate Django Secret Key

On your computer, run:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output - you'll need it next.

### 2. Set Application Settings

```
Azure Portal → Web App → Configuration (left sidebar) → Application settings

Click "+ New application setting" for each:

DJANGO_SECRET_KEY
Value: [paste the secret key from step 1]

DJANGO_DEBUG
Value: 0

AZURE_ALLOW_ALL_HOSTS
Value: 1

MYSQL_HOST
Value: dml-mysql-server.mysql.database.azure.com

MYSQL_PORT
Value: 3306

MYSQL_DATABASE
Value: dml_marketing_middleware

MYSQL_USER
Value: dmladmin

MYSQL_PASSWORD
Value: [your MySQL admin password]

MYSQL_SSL
Value: 1

SERVICEBUS_CONNECTION_STRING
Value: [get from Service Bus → Shared access policies → RootManageSharedAccessKey]

SERVICEBUS_QUEUE_NAME
Value: webform-leads

TOTAL_EXPERT_CLIENT_ID
Value: [from Total Expert]

TOTAL_EXPERT_CLIENT_SECRET
Value: [from Total Expert]

TOTAL_EXPERT_API_URL
Value: https://api.totalexpert.net

DJANGO_CREATE_SUPERUSER
Value: 1

DJANGO_SUPERUSER_USERNAME
Value: marketingadmin

DJANGO_SUPERUSER_EMAIL
Value: jwalker@directmortgageloans.com

DJANGO_SUPERUSER_PASSWORD
Value: [create a secure password - SAVE THIS]

Click: Save
Click: Continue (when prompted about restart)
```

### 3. Set Startup Command

```
Same Configuration page → General settings tab

Startup Command:
bash /home/site/wwwroot/startup.sh

Click: Save
```

---

## Phase 5: Update GitHub Repository (5 minutes)

### 1. Back Up Old Code (Optional)

```bash
# In your local dml-marketing-middleware repo
git checkout -b backup-old-code
git push origin backup-old-code
git checkout main
```

### 2. Replace with New Code

```bash
# Delete all files except .git/
rm -rf *
rm -rf .github  # We'll replace this too

# Copy new files from the clean build
# (I'll provide these files in the next message)

# Stage all files
git add .

# Commit
git commit -m "Complete rebuild with MySQL support"

# Push to GitHub
git push origin main
```

This will trigger the GitHub Actions deployment automatically!

---

## Phase 6: Verify Deployment (10 minutes)

### 1. Monitor Deployment

```
GitHub → Your Repository → Actions tab
Watch the deployment workflow run
```

### 2. Check Application Logs

```bash
# Using Azure CLI
az webapp log tail --name middleware-api-v2 --resource-group dml-marketing-middleware

# Or in Azure Portal
Web App → Log stream (left sidebar)
```

Look for:
```
Running migrations...
Superuser 'marketingadmin' created successfully
Database: django.db.backends.mysql @ dml-mysql-server.mysql.database.azure.com:3306/dml_marketing_middleware
Starting Gunicorn...
```

### 3. Test Health Endpoint

```bash
curl https://middleware-api-v2-[random].azurewebsites.net/health
```

Expected response:
```json
{"status":"healthy","service":"dml-marketing-middleware"}
```

### 4. Access Django Admin

```
1. Go to: https://[your-app-url]/admin
2. Login with:
   - Username: marketingadmin
   - Password: [your superuser password]
```

---

## Phase 7: Add First Loan Officer (5 minutes)

### Via Django Admin:

```
1. Login to /admin
2. Click "Loan Officers"
3. Click "Add Loan Officer"
4. Fill in:
   - Slug: john-smith (lowercase, matches URL)
   - First name: John
   - Last name: Smith
   - Email: john.smith@directmortgageloans.com
   - Phone: 555-1234
   - TE Owner ID: [from Total Expert]
   - Is active: ✓
5. Click "Save"
```

---

## Phase 8: Test the API (5 minutes)

### Test Lead Submission:

```bash
curl -X POST https://[your-app-url]/api/v1/leads/webform \
  -H "Content-Type: application/json" \
  -d '{
    "lo_slug": "john-smith",
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "555-9999",
    "page_url": "https://directmortgageloans.com/john-smith",
    "referrer": "https://google.com"
  }'
```

Expected response:
```json
{
  "success": true,
  "id": "a1b2c3d4-e5f6-...",
  "status": "queued",
  "message": "Lead received and queued for processing"
}
```

### Verify in Admin:

```
1. Django Admin → Lead Submissions
2. You should see the test lead
3. Status should be "Queued" (blue badge)
```

### Verify in Service Bus:

```
Azure Portal → Service Bus → Queues → webform-leads → Service Bus Explorer
You should see 1 message in the queue
```

---

## Troubleshooting

### Issue: Database Connection Failed

```
Solution:
1. Azure Portal → MySQL Server → Networking
2. Ensure "Allow Azure services" rule exists
3. Connection security → SSL enforcement → Enabled
```

### Issue: Migrations Failed

```
Solution:
1. Check logs: az webapp log tail ...
2. Verify all MYSQL_* environment variables are set
3. Test connection from SSH console:
   mysql -h [MYSQL_HOST] -u [MYSQL_USER] -p
```

### Issue: GitHub Actions Fails

```
Solution:
1. GitHub → Repository → Settings → Secrets
2. Ensure AZUREAPPSERVICE_PUBLISHPROFILE exists
3. If not, get from: Azure Portal → Web App → Deployment Center → Manage publish profile
4. Add as secret: AZUREAPPSERVICE_PUBLISHPROFILE
```

---

## Success Checklist

- [ ] MySQL database created and accessible
- [ ] Web App deployed and running
- [ ] All environment variables configured
- [ ] GitHub Actions deployment successful
- [ ] Health endpoint returns 200 OK
- [ ] Django admin accessible
- [ ] Superuser can login
- [ ] Test loan officer created
- [ ] Test API call succeeds
- [ ] Lead appears in admin
- [ ] Message appears in Service Bus queue

---

## Next Steps

1. **Import Existing Loan Officers**: Create all ~100 LOs via Django admin or management command
2. **Configure Formidable**: Update webhook URL to new endpoint
3. **Test with Real Forms**: Submit test leads from actual webforms
4. **Build Service Bus Worker**: Process queued leads and sync to Total Expert
5. **Set up Monitoring**: Configure Azure alerts and dashboards

---

## Quick Reference

**Web App URL**: https://middleware-api-v2-[random].azurewebsites.net
**Admin URL**: [Web App URL]/admin
**API Endpoint**: [Web App URL]/api/v1/leads/webform
**Health Check**: [Web App URL]/health

**MySQL Server**: dml-mysql-server.mysql.database.azure.com
**Database**: dml_marketing_middleware
**Service Bus Queue**: webform-leads

---

Need help? Contact Jadon Walker (jwalker@directmortgageloans.com)
