# ABBK LeadEngine — User Management Guide

## Authentication System Overview

The platform uses **admin-controlled authentication** — no public signup allowed. Only administrators can create user accounts, ensuring complete control over who accesses the system.

---

## 🔐 How Authentication Works

### Login Process
1. User visits `http://localhost:5173`
2. Enters email and password
3. System validates credentials
4. If valid, user receives a JWT token and is logged in
5. If account is inactive, login is denied

### No Public Signup
- Users **cannot** register themselves
- No "Create Account" or "Sign Up" button exists
- All accounts must be created by an administrator
- Login page shows: "Don't have an account? Contact your admin to create one for you."

---

## 👥 User Roles & Permissions

### 1. Admin 👑
**Full platform access + user management**
- View and manage all leads and scores
- Access all reports and analytics
- Create, edit, and delete user accounts
- Change user roles and permissions
- Activate/deactivate accounts
- Access User Management page (Shield icon in sidebar)

### 2. Manager 📊
**Complete business operations access**
- View all leads and their scores
- Access all analytics and reports
- View sales pipeline and activities
- Receive notifications for hot leads
- **Cannot**: Manage users or change system settings

### 3. Sales 💼
**Limited to assigned leads only**
- View only leads assigned to them
- See scores for their assigned leads
- Update lead status and activities
- **Cannot**: See other users' leads, manage users, or access full analytics

### 4. Viewer 👁️
**Read-only access**
- View lead information (read-only)
- **Cannot**: Edit leads, see scores, manage users, or export data
- Useful for stakeholders who need visibility without editing rights

---

## 🛠️ Admin: How to Manage Users

### Accessing User Management
1. Login as admin (`admin@abbk.tn` / `admin123`)
2. Click **User Management** (Shield icon) in the sidebar
3. You'll see all users listed with their details

### Creating a New User

**Via Web Interface:**
1. Click **"Create User"** button
2. Fill in the form:
   - **Email**: User's email address (must be unique)
   - **Full Name**: User's display name
   - **Password**: Initial password (user should change this)
   - **Role**: Select Admin, Manager, Sales, or Viewer
3. Click **"Create User"**
4. The user can now login with the credentials you provided

**Via API:**
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@abbk.tn",
    "full_name": "New User",
    "password": "secure123",
    "role": "manager"
  }'
```

### Editing a User

**Via Web Interface:**
1. Find the user in the list
2. Click **"Edit"** button
3. Modify any fields:
   - Email
   - Full Name
   - Password (leave blank to keep current password)
   - Role
4. Click **"Update User"**

**Via API:**
```bash
curl -X PATCH http://localhost:8000/api/users/3 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "role": "sales"
  }'
```

### Deactivating a User

**Why deactivate instead of delete?**
- Preserves user's activity history
- Can be reactivated later if needed
- Safer than permanent deletion

**Via Web Interface:**
1. Find the user
2. Click **"Deactivate"** button
3. User can no longer login
4. Click **"Activate"** to restore access

**Via API:**
```bash
curl -X PATCH http://localhost:8000/api/users/3 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

### Deleting a User

**⚠️ Warning**: This is permanent and cannot be undone!

**Via Web Interface:**
1. Find the user
2. Click **"Delete"** button (red)
3. Confirm deletion in the popup
4. User and all their data are permanently removed

**Restrictions:**
- Admins cannot delete themselves
- System prevents accidental self-deletion

**Via API:**
```bash
curl -X DELETE http://localhost:8000/api/users/3 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 User Management Best Practices

### For ABBK Business Manager:

1. **Create accounts before onboarding**
   - Create account for new employee
   - Send them their email and initial password
   - Ask them to change password on first login (future feature)

2. **Use appropriate roles**
   - Sales team → **Sales** role (only see their assigned leads)
   - Business managers → **Manager** role (see everything)
   - C-level executives → **Viewer** role (read-only oversight)
   - IT/System admin → **Admin** role (one person only)

3. **Deactivate instead of delete**
   - When employee leaves, deactivate their account
   - Preserves their activity history
   - Can reactivate if they return

4. **Regular access review**
   - Monthly: Review who has access
   - Check if all active users still need access
   - Update roles as responsibilities change

---

## 🔑 Default Accounts (Demo)

| Email | Password | Role | Purpose |
|-------|----------|------|---------|
| admin@abbk.tn | admin123 | Admin | System administrator |
| sales@abbk.tn | sales123 | Sales | Demo sales user |
| manager@abbk.tn | manager123 | Manager | Demo business manager |

**⚠️ IMPORTANT FOR PRODUCTION:**
1. Change all default passwords immediately
2. Use strong passwords (12+ characters, mixed case, numbers, symbols)
3. Delete demo accounts you don't need

---

## 🚀 Quick Start for New Users

### As Admin (First Time Setup):
```bash
1. Login: admin@abbk.tn / admin123
2. Go to User Management (Shield icon)
3. Create accounts for your team:
   - Business Manager → manager role
   - Sales team → sales role
   - Stakeholders → viewer role
4. Send credentials to each user
5. Change your admin password
```

### As New User:
```bash
1. Receive email and password from admin
2. Visit: http://localhost:5173
3. Login with your credentials
4. Start using the platform based on your role
```

---

## 🔧 API Endpoints Reference

All user management endpoints require **Admin role** and valid JWT token.

### List All Users
```http
GET /api/users/
Authorization: Bearer {token}
```

### Get Single User
```http
GET /api/users/{user_id}
Authorization: Bearer {token}
```

### Create User
```http
POST /api/users/
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "user@abbk.tn",
  "full_name": "Full Name",
  "password": "password123",
  "role": "manager"
}
```

### Update User
```http
PATCH /api/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "New Name",
  "role": "sales",
  "is_active": true
}
```

### Delete User
```http
DELETE /api/users/{user_id}
Authorization: Bearer {token}
```

---

## 🐛 Troubleshooting

### "Account is inactive" error
- The account has been deactivated by an admin
- Contact your administrator to reactivate your account

### "Incorrect email or password"
- Double-check your email and password
- Passwords are case-sensitive
- Contact admin if you forgot your password

### "Forbidden" error when accessing User Management
- Only Admin role can access user management
- Check your role in the sidebar (shows under your name)

### Cannot delete a user
- You cannot delete yourself (admin self-protection)
- User might have dependencies in the database
- Try deactivating instead of deleting

---

## 📊 Current System Status

✅ **Backend API**: Fully implemented and tested
✅ **Frontend UI**: Complete user management page with modals
✅ **Role-Based Access**: Admin-only access enforced
✅ **CRUD Operations**: Create, Read, Update, Delete all working
✅ **Security**: JWT authentication, password hashing, RBAC
✅ **Validation**: Email uniqueness, required fields, role validation

---

## 🎯 Next Steps (Future Enhancements)

1. **Password reset flow**: "Forgot password" functionality
2. **Force password change**: On first login
3. **Password strength requirements**: Enforce strong passwords
4. **User activity logs**: Track who did what and when
5. **Bulk user import**: CSV import for creating multiple users
6. **Email notifications**: Auto-send credentials to new users
7. **Session management**: View and revoke active sessions
8. **Two-factor authentication**: Optional 2FA for admin accounts

---

## 📞 Support

For issues or questions about user management:
- Developer: Rayhane Nouri
- Email: rayhane.nouri1@gmail.com
- Documentation: This guide
- API Docs: http://localhost:8000/docs
