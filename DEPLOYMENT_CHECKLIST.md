# Deployment Checklist

## Pre-Deployment

- [ ] Read QUICK_START.md
- [ ] Read DEPLOYMENT_GUIDE.md  
- [ ] Back up current GitHub repo (optional)
- [ ] Have Azure Portal access
- [ ] Have Total Expert credentials ready

---

## Azure MySQL Setup

- [ ] Created MySQL Flexible Server
  - Server name: ___________________
  - Admin user: ___________________
  - Admin password saved: [ ]
- [ ] Created database: dml_marketing_middleware
- [ ] Configured firewall rules (Allow Azure services)
- [ ] Tested connection

---

## Web App Setup

- [ ] Deleted old middleware-api (if needed)
- [ ] Created new Web App
  - App name: ___________________
  - Runtime: Python 3.11
  - Region: East US 2
- [ ] Connected to GitHub repository
  - Repo: jadonwalker0/dml-marketing-middleware
  - Branch: main

---

## Environment Variables

In Azure Portal → Web App → Configuration:

### Required (Critical)
- [ ] DJANGO_SECRET_KEY (generated)
- [ ] MYSQL_HOST
- [ ] MYSQL_DATABASE
- [ ] MYSQL_USER
- [ ] MYSQL_PASSWORD
- [ ] SERVICEBUS_CONNECTION_STRING
- [ ] SERVICEBUS_QUEUE_NAME

### Optional (Recommended)
- [ ] DJANGO_DEBUG (set to 0)
- [ ] AZURE_ALLOW_ALL_HOSTS (set to 1)
- [ ] MYSQL_SSL (set to 1)
- [ ] TOTAL_EXPERT_CLIENT_ID
- [ ] TOTAL_EXPERT_CLIENT_SECRET
- [ ] DJANGO_CREATE_SUPERUSER (set to 1)
- [ ] DJANGO_SUPERUSER_USERNAME
- [ ] DJANGO_SUPERUSER_EMAIL
- [ ] DJANGO_SUPERUSER_PASSWORD

### Startup Command
- [ ] Set to: `bash /home/site/wwwroot/startup.sh`

---

## Code Deployment

- [ ] Replaced local code with new files
- [ ] Committed to Git
- [ ] Pushed to GitHub main branch
- [ ] GitHub Actions workflow completed successfully
- [ ] No errors in deployment logs

---

## Verification

### Health Check
- [ ] GET /health returns 200 OK
  - URL: https://___________________/health

### Django Admin
- [ ] Can access /admin
  - URL: https://___________________/admin
- [ ] Can login with superuser credentials
- [ ] Can see Loan Officers section
- [ ] Can see Lead Submissions section

### Database
- [ ] Migrations completed successfully
- [ ] Tables created in MySQL
- [ ] Can view data in Django admin

---

## Testing

### Create Test Loan Officer
- [ ] Added via Django admin
  - Slug: ___________________
  - Is Active: ✓

### Test API Endpoint
- [ ] POST /api/v1/leads/webform succeeds
- [ ] Returns 201 status code
- [ ] Returns success: true
- [ ] Lead appears in Django admin
- [ ] Lead status is "Queued"

### Service Bus
- [ ] Message appears in webform-leads queue
- [ ] No errors in Service Bus logs

---

## Production Readiness

### Data Import
- [ ] Prepared CSV with all loan officers
- [ ] Ran import_loan_officers command
- [ ] Verified all LOs imported correctly
- [ ] All LOs marked as active

### Formidable Configuration
- [ ] Updated webhook URL to new endpoint
- [ ] Tested with real webform
- [ ] Lead successfully captured

### Monitoring
- [ ] Set up Azure Application Insights (optional)
- [ ] Configured alerts for errors (optional)
- [ ] Set up log retention (optional)

---

## Documentation

- [ ] Updated team documentation with new URLs
- [ ] Shared admin credentials securely
- [ ] Documented any custom configurations
- [ ] Created runbook for common issues

---

## Rollback Plan

In case of issues:

- [ ] Keep old code in backup branch
- [ ] Document rollback procedure
- [ ] Know how to revert environment variables
- [ ] Have backup of database (if needed)

---

## Post-Deployment

### Week 1
- [ ] Monitor logs daily
- [ ] Check lead submission volume
- [ ] Verify Service Bus queue processing
- [ ] Address any errors promptly

### Week 2-4
- [ ] Build Service Bus worker for CRM sync
- [ ] Implement Total Expert integration
- [ ] Add retry logic for failed syncs
- [ ] Create analytics dashboard

---

## Support Contacts

**Azure Issues**: 
- Portal: https://portal.azure.com
- Support: [ticket system]

**Django/Python Issues**:
- Developer: Jadon Walker
- Email: jwalker@directmortgageloans.com

**Total Expert Issues**:
- API Docs: https://documenter.getpostman.com/view/1929166/total-expert-public-api/6Z2RYyU
- Support: [TE support contact]

---

## Notes

Date deployed: ___________________

Issues encountered:
_____________________________________
_____________________________________
_____________________________________

Resolutions:
_____________________________________
_____________________________________
_____________________________________

---

## Final Sign-Off

- [ ] All systems operational
- [ ] Team trained on new system
- [ ] Documentation complete
- [ ] Ready for production traffic

**Deployed by**: ___________________
**Date**: ___________________
**Verified by**: ___________________
