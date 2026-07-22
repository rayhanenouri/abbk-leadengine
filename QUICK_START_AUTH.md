# 🚀 Quick Start — User Management

## For ABBK Business Manager (5-Minute Guide)

### Login to Platform
```
URL: http://localhost:5173
Email: admin@abbk.tn
Password: admin123
```

### Create Your First User (3 Steps)

**Step 1: Open User Management**
- After login, look at left sidebar
- Click **"User Management"** (Shield icon 🛡️)

**Step 2: Create User**
- Click blue **"Create User"** button
- Fill the form:
  ```
  Email: sales@abbk.tn
  Full Name: Sales Representative
  Password: sales123
  Role: Select "Sales" (💼)
  ```
- Click **"Create User"**

**Step 3: Share Credentials**
- Tell the user:
  - "Go to http://localhost:5173"
  - "Login with sales@abbk.tn / sales123"
  - "You're ready to work!"

**Done!** The user can now login and start using the platform.

---

## Quick Actions

### Change Someone's Role
```
1. Find user in list
2. Click "Edit"
3. Select new role (Admin/Manager/Sales/Viewer)
4. Click "Update User"
```

### Temporarily Block Access
```
1. Find user in list
2. Click "Deactivate" (yellow button)
3. They cannot login anymore
4. Click "Activate" to restore access
```

### Remove User Permanently
```
1. Find user in list
2. Click "Delete" (red button)
3. Confirm deletion
⚠️ This cannot be undone!
```

---

## The 4 Roles Explained

| Role | Icon | What They Can Do |
|------|------|------------------|
| **Admin** | 👑 | Everything + manage users |
| **Manager** | 📊 | See all leads + reports |
| **Sales** | 💼 | Only their assigned leads |
| **Viewer** | 👁️ | Read-only, no editing |

**Pro Tip:** Most sales team members should be "Sales" role, business managers should be "Manager" role.

---

## Common Scenarios

### New Employee Joins
```
Create User → Role: Sales → Share credentials
```

### Promote Sales to Manager
```
Edit User → Change role to Manager → Update
```

### Employee Leaves Company
```
Click "Deactivate" (keeps history for records)
```

### Forgot Password
```
Edit User → Enter new password → Update User
```

### Someone Needs Read-Only Access
```
Create User → Role: Viewer → Share credentials
```

---

## Test Users (Already Created)

| Email | Password | Role | Use For |
|-------|----------|------|---------|
| admin@abbk.tn | admin123 | Admin | You (system admin) |
| sales@abbk.tn | sales123 | Sales | Test sales user |
| manager@abbk.tn | manager123 | Manager | Test manager access |

**Change these passwords in production!**

---

## FAQ

**Q: Can users sign up themselves?**
A: No. Only you (admin) can create accounts. This ensures control.

**Q: How do I change my own password?**
A: Edit your own user account from the user list.

**Q: What happens if I delete a user?**
A: Permanently removed. Better to "Deactivate" instead.

**Q: Can I have multiple admins?**
A: Yes! Just create a user and select "Admin" role.

**Q: Do I need internet to create users?**
A: No. Everything runs locally on your network.

---

## Need Help?

- **Full Guide**: See `USER_MANAGEMENT_GUIDE.md`
- **Developer**: Rayhane Nouri (rayhane.nouri1@gmail.com)
- **Technical Docs**: http://localhost:8000/docs

---

**Remember:** Only admins can see the "User Management" page. Other roles won't see it in their sidebar.
