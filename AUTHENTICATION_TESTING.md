# Authentication System Testing Guide

## ✅ Implementation Complete

All authentication and user onboarding features have been successfully implemented and tested.

## Features Implemented

### 1. User Self-Registration (Signup)
- **Endpoint**: `POST /api/auth/signup`
- **Page**: `/signup` in frontend
- **Features**:
  - Full name, email, password, company/role fields
  - Password validation (minimum 8 characters)
  - Confirm password field
  - Creates account with `role=viewer` and `is_active=false`
  - Professional UI matching login page design
  - Success confirmation screen
  - Link back to login page

### 2. Admin User Management
- **Endpoints**:
  - `GET /api/users/pending` - List users awaiting approval
  - `PUT /api/users/{id}/approve` - Approve user and assign role
  - `PUT /api/users/{id}/role` - Change existing user role
  - `DELETE /api/users/{id}` - Delete user
- **Page**: `/users` (Admin only)
- **Features**:
  - Pending users section with approve/reject buttons
  - Active users list
  - Role selector dropdown for active users
  - Approval modal to assign initial role
  - User activation/deactivation
  - User deletion with confirmation

### 3. Role-Based Access Control
- **Roles**:
  - **Viewer**: Dashboard and lead list only, no scores visible
  - **Sales**: Assigned leads with scores and details
  - **Manager**: Full access except user management
  - **Admin**: Complete platform control including user management
- **Implementation**:
  - Sidebar automatically hides "User Management" for non-admin users
  - Current user data fetched on login via `GET /api/auth/me`
  - User object passed to all Sidebar instances

### 4. Welcome Screen for New Users
- **Component**: `WelcomeModal.jsx`
- **Features**:
  - Shows on first login only (tracked in localStorage)
  - Displays user's assigned role and permissions
  - Lists what they can and cannot do
  - Role-specific icons and colors
  - "Get Started" button to close and proceed to dashboard

### 5. Enhanced Login Page
- **Features**:
  - "Request Access" button linking to signup
  - "Forgot password? Contact your administrator" message
  - Maintains existing professional design

## Testing Instructions

### Test 1: Complete Signup Flow
1. Navigate to `http://localhost:5173`
2. Click "Request Access" button on login page
3. Fill out signup form:
   - Full Name: "Jane Smith"
   - Email: "jane.smith@company.com"
   - Company/Role: "Sales Manager" (optional)
   - Password: "password123"
   - Confirm Password: "password123"
4. Click "Request Access"
5. ✅ **Expected**: Success screen showing "Request Submitted!"
6. Click "Back to Login"
7. Try to login with new credentials
8. ✅ **Expected**: Error "Account is inactive"

### Test 2: Admin Approval Flow
1. Login as admin: `admin@abbk.tn` / `admin123`
2. Click "User Management" in sidebar
3. ✅ **Expected**: See "Pending Approval" section with Jane Smith
4. Click "Approve" button
5. ✅ **Expected**: Modal opens showing role selection
6. Select role "Sales"
7. Click "Approve & Activate"
8. ✅ **Expected**: Jane moves from pending to active users list

### Test 3: New User First Login
1. Logout from admin account
2. Login as Jane: `jane.smith@company.com` / `password123`
3. ✅ **Expected**: Welcome modal appears
4. ✅ **Expected**: Shows "Sales" role with permissions list
5. Click "Go to Dashboard"
6. ✅ **Expected**: Modal closes, dashboard loads
7. Logout and login again
8. ✅ **Expected**: Welcome modal does NOT appear (shown once only)

### Test 4: Role-Based Navigation
1. Login as viewer account
2. ✅ **Expected**: Sidebar does NOT show "User Management"
3. Logout and login as admin
4. ✅ **Expected**: Sidebar SHOWS "User Management"

### Test 5: Admin Change User Role
1. Login as admin: `admin@abbk.tn` / `admin123`
2. Go to User Management
3. Find Jane Smith in active users
4. Click role dropdown, select "Manager"
5. ✅ **Expected**: Role updates immediately
6. Logout and login as Jane
7. ✅ **Expected**: Jane now has manager-level access

### Test 6: Admin Cannot Change Own Role
1. Login as admin
2. Go to User Management
3. Try to change admin's own role via API:
   ```bash
   curl -X PUT http://localhost:8000/api/users/1/role \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"role": "viewer"}'
   ```
4. ✅ **Expected**: Error "You cannot change your own role"

### Test 7: Pending User Cannot Login
1. Create new signup: `test2@company.com` / `password123`
2. Do NOT approve the account
3. Try to login with these credentials
4. ✅ **Expected**: Error "Account is inactive"

## Backend API Testing (Already Verified)

All endpoints tested successfully via curl:

```bash
# 1. Signup
✅ POST /api/auth/signup
   → Creates user with is_active=false, role=viewer

# 2. List pending users (admin only)
✅ GET /api/users/pending
   → Returns all users where is_active=false

# 3. Approve user (admin only)
✅ PUT /api/users/5/approve
   Body: {"role": "sales"}
   → Sets is_active=true, assigns role

# 4. Change role (admin only)
✅ PUT /api/users/5/role
   Body: {"role": "manager"}
   → Updates user role

# 5. Get current user
✅ GET /api/auth/me
   → Returns logged-in user profile with role
```

## Files Modified/Created

### Backend
- `backend/app/schemas/auth.py` - Added `SignupRequest` schema
- `backend/app/schemas/user.py` - Added `ApproveUserRequest`, `UpdateRoleRequest`
- `backend/app/api/routes/auth.py` - Added `POST /signup` endpoint
- `backend/app/api/routes/users.py` - Added pending users, approve, role change endpoints

### Frontend
- `frontend/src/pages/Signup.jsx` - NEW: Signup page
- `frontend/src/pages/LoginV2.jsx` - Added signup link and forgot password text
- `frontend/src/pages/UserManagement.jsx` - Added pending users section and approval modal
- `frontend/src/components/WelcomeModal.jsx` - NEW: First-time user welcome screen
- `frontend/src/App.jsx` - Added signup route, user fetching, welcome modal integration

## Security Features
- Passwords hashed with bcrypt before storage
- JWT tokens required for all authenticated endpoints
- Role-based endpoint protection (admin-only routes)
- Account activation required before login
- Password minimum length validation
- Email uniqueness validation

## User Experience Flow
1. New user visits platform → Clicks "Request Access"
2. Fills signup form → Sees success confirmation
3. Admin receives pending request notification (visible in User Management)
4. Admin approves and assigns appropriate role
5. User logs in → Sees welcome modal explaining their permissions
6. User proceeds to dashboard with role-appropriate access

## Production Ready ✓
This authentication system is ready for the ABBK team to use. The business manager can now:
- Approve team members requesting access
- Assign appropriate roles based on job function
- Change roles as team structure evolves
- Manage active/inactive users
- Each user sees exactly what they should based on their role
