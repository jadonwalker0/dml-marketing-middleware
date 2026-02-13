# Quick Start Guide

## What's Changed?

✅ **Completely rebuilt from scratch with MySQL** (no more SQLite)
✅ **Clean project structure** (removed duplicate LoanOfficer models)
✅ **Production-ready configuration** for Azure
✅ **Comprehensive documentation** and deployment guides
✅ **Better error handling and logging**
✅ **Management commands** for bulk operations

---

## Deploy in 30 Minutes

### Step 1: Create MySQL Database (5 min)
```
Azure Portal → Create MySQL Flexible Server
- Name: dml-mysql-server
- Database: dml_marketing_middleware
- User: dmladmin
- Password: [save this!]
```

### Step 2: Delete Old Web App (1 min)
```
Azure Portal → middleware-api → Delete
(Keep Service Bus!)
```

### Step 3: Create New Web App (3 min)
```
Azure Portal → Create Web App
- Name: middleware-api-v2
- Runtime: Python 3.11
- Region: East US 2
```

### Step 4: Configure Variables (10 min)
```
Web App → Configuration → Application settings

Add these (see DEPLOYMENT_GUIDE.md for all values):
- DJANGO_SECRET_KEY
- MYSQL_HOST
- MYSQL_DATABASE
- MYSQL_USER
- MYSQL_PASSWORD
- SERVICEBUS_CONNECTION_STRING
- [and others...]

General settings → Startup Command:
bash /home/site/wwwroot/startup.sh
```

### Step 5: Push New Code (5 min)
```bash
# In your local repo
git checkout main
# Replace all files with new code
git add .
git commit -m "Rebuild with MySQL"
git push origin main
```

### Step 6: Verify (5 min)
```bash
# Test health endpoint
curl https://[your-app]/health

# Login to admin
https://[your-app]/admin
```

### Step 7: Test API (1 min)
```bash
# Add a loan officer in admin first, then:
curl -X POST https://[your-app]/api/v1/leads/webform \
  -H "Content-Type: application/json" \
  -d '{"lo_slug":"test-user","first_name":"Test","last_name":"User","email":"test@test.com","phone":"555-1234"}'
```

---

## Files Included

```
dml-marketing-middleware-mysql/
├── README.md                    # Complete documentation
├── DEPLOYMENT_GUIDE.md          # Step-by-step deployment
├── QUICK_START.md               # This file
├── requirements.txt             # Python dependencies
├── manage.py                    # Django management
├── startup.sh                   # Azure startup script
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── loan_officers_template.csv  # CSV import template
├── .github/
│   └── workflows/
│       └── main_middleware-api.yml  # GitHub Actions
├── config/                      # Django settings
│   ├── settings.py             # MySQL configuration
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                        # Loan Officers app
│   ├── models.py               # LoanOfficer model
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── import_loan_officers.py
└── leads/                       # Leads app
    ├── models.py                # LeadSubmission model
    ├── views.py                 # API endpoints
    ├── admin.py
    ├── servicebus.py            # Service Bus integration
    └── urls.py
```

---

## Key Features

### API Endpoint
```
POST /api/v1/leads/webform
{
  "lo_slug": "john-smith",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "phone": "555-1234"
}
```

### Django Admin
- Manage loan officers
- View all lead submissions
- Color-coded status badges
- Search and filter capabilities

### Bulk Import
```bash
python manage.py import_loan_officers loan_officers.csv
```

---

## What's Fixed?

1. ❌ **Old**: SQLite with persistence issues
   ✅ **New**: MySQL database on Azure

2. ❌ **Old**: Two conflicting LoanOfficer models
   ✅ **New**: Single source of truth in core app

3. ❌ **Old**: Import errors between apps
   ✅ **New**: Clean imports, proper structure

4. ❌ **Old**: Confusing deployment
   ✅ **New**: Clear documentation and scripts

5. ❌ **Old**: No way to bulk import LOs
   ✅ **New**: CSV import command included

---

## Next Steps After Deployment

1. **Import All Loan Officers**
   - Export from current system to CSV
   - Use `import_loan_officers` command

2. **Update Formidable Webhooks**
   - Point to new `/api/v1/leads/webform` endpoint

3. **Build Service Bus Worker**
   - Process queued leads
   - Sync to Total Expert CRM

4. **Set Up Monitoring**
   - Azure Application Insights
   - Alert on errors

---

## Support

**Developer**: Jadon Walker
**Email**: jwalker@directmortgageloans.com
**Repo**: https://github.com/jadonwalker0/dml-marketing-middleware

**Documentation**:
- `README.md` - Complete technical documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment steps
- `.env.example` - All environment variables

**Need help?** Open an issue on GitHub or contact Jadon directly.

---

## Success Checklist

- [ ] MySQL database created
- [ ] New web app deployed
- [ ] Environment variables configured
- [ ] Code pushed to GitHub
- [ ] Health endpoint works
- [ ] Admin login works
- [ ] Test loan officer added
- [ ] Test API call succeeds
- [ ] Lead shows in admin
- [ ] Message in Service Bus queue

**All green? You're ready to go! 🚀**
