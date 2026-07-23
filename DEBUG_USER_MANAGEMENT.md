# Debugging: User Management Not Showing in Sidebar

## The Fix Applied

I've fixed the issue where "User Management" wasn't showing in the admin sidebar. The problem was:

**Root Cause**: The `currentUser` prop wasn't being passed from `App.jsx` → `DashboardPro` → `Sidebar`, so the Sidebar couldn't check if the user has admin role.

**Files Fixed**:
1. `frontend/src/App.jsx` - Now passes `currentUser={currentUser}` to `DashboardPro`
2. `frontend/src/pages/DashboardPro.jsx` - Now receives and passes `currentUser` to both Sidebar instances

## How to Test

### Step 1: Open the App
Navigate to: http://localhost:5173

### Step 2: Login as Admin
- Email: `admin@abbk.tn`
- Password: `admin123`

### Step 3: Check the Sidebar
Look at the **left sidebar**, scroll to the **bottom section** (below Tools).

You should see:
```
┌─────────────────────┐
│ 🔔 Notifications    │
│ 📄 Export Reports   │
│ 🛡️ User Management  │ ← This should be visible now!
└─────────────────────┘
```

### Step 4: Click User Management
Click on "User Management" and you should see:
- Pending Users section (if any signups exist)
- Active Users section
- "Create User" button

## Debugging if Still Not Working

### Check 1: Verify User Data is Loading

Open browser console (F12) and type:
```javascript
// Check if user data is in state
console.log('Token:', localStorage.getItem('token'));
```

Then refresh the page and watch the Network tab:
- You should see a request to `/api/auth/me`
- It should return your user data with `"role": "admin"`

### Check 2: Add Console Logging

Open browser console (F12) and add this to check what the Sidebar is receiving:
```javascript
// This will help debug
window.addEventListener('load', () => {
  setTimeout(() => {
    console.log('Current user should be loaded now');
  }, 1000);
});
```

### Check 3: Verify the Admin User in Database

Run this in terminal to confirm the admin user exists:
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@abbk.tn", "password": "admin123"}' \
  -s | jq -r '.access_token')

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq
```

Expected output:
```json
{
  "id": 1,
  "email": "admin@abbk.tn",
  "full_name": "Admin User",
  "role": "admin",  ← Must be "admin"
  "is_active": true,
  "permissions": {},
  "created_at": "..."
}
```

### Check 4: Clear Cache and Reload

Sometimes the browser caches the old JavaScript:
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Choose "Empty Cache and Hard Reload"
4. Login again

### Check 5: Verify Docker Frontend Rebuilt

Check if the frontend container rebuilt successfully:
```bash
docker compose logs frontend --tail 50 | grep -i "hmr\|error"
```

You should see Hot Module Replacement (HMR) updates with no errors.

### Check 6: Restart Frontend Container

If all else fails, restart the frontend:
```bash
docker compose restart frontend
docker compose logs frontend -f
```

Wait for "ready in" message, then refresh browser.

## Common Issues

### Issue 1: "User Management shows for non-admin users"
**Problem**: Everyone sees User Management  
**Cause**: The role check is inverted  
**Fix**: Check `Sidebar.jsx` line 199 should be:
```javascript
if (item.adminOnly && user?.role !== 'admin') {
  return null;
}
```

### Issue 2: "User Management never shows, even for admin"
**Problem**: Sidebar never receives user data  
**Cause**: `currentUser` is null or undefined  
**Fix**: Check the flow:
1. App.jsx calls `fetchCurrentUser()` on login ✓
2. Sets `currentUser` state ✓
3. Passes to DashboardPro ✓
4. DashboardPro passes to Sidebar ✓

### Issue 3: "I can see User Management but clicking does nothing"
**Problem**: Route exists but component not rendering  
**Cause**: App.jsx switch statement missing 'users' case  
**Fix**: Check App.jsx has:
```javascript
case 'users':
  return (
    <div className="flex h-screen bg-neutral-50 overflow-hidden">
      <Sidebar ... user={currentUser} />
      <div className="flex-1 overflow-auto w-full">
        <UserManagement />
      </div>
    </div>
  )
```

## Expected Behavior After Fix

✅ **Admin user**: Sees "User Management" in sidebar  
✅ **Manager user**: Does NOT see "User Management"  
✅ **Sales user**: Does NOT see "User Management"  
✅ **Viewer user**: Does NOT see "User Management"  

## Test with Different Roles

Create test users with different roles:

```bash
# Get admin token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@abbk.tn", "password": "admin123"}' \
  -s | jq -r '.access_token')

# Create a manager user
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager.test@abbk.tn",
    "full_name": "Test Manager",
    "password": "password123",
    "role": "manager"
  }' | jq

# Create a sales user
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sales.test@abbk.tn",
    "full_name": "Test Sales",
    "password": "password123",
    "role": "sales"
  }' | jq
```

Then test:
1. Login as `manager.test@abbk.tn` / `password123` → No "User Management"
2. Login as `sales.test@abbk.tn` / `password123` → No "User Management"
3. Login as `admin@abbk.tn` / `admin123` → SHOWS "User Management" ✓

## Still Having Issues?

If none of the above works, share:
1. Browser console errors (F12 → Console tab)
2. Network requests to `/api/auth/me` (F12 → Network tab)
3. Output of the database check command (Check 3)

The issue should be resolved now! The currentUser prop is properly flowing through the component tree.
