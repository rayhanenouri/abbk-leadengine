import { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import Landing from './pages/Landing'
import LoginV2 from './pages/LoginV2'
import Signup from './pages/Signup'
import DashboardPro from './pages/DashboardPro'
import AnalyticsEnterprise from './pages/AnalyticsEnterprise'
import Leads from './pages/Leads'
import SalesPipeline from './pages/SalesPipeline'
import Activities from './pages/Activities'
import LiveSignals from './pages/LiveSignals'
import SmartSearch from './pages/SmartSearch'
import ScoreEngine from './pages/ScoreEngine'
import DataSources from './pages/DataSources'
import Notifications from './pages/Notifications'
import ExportReports from './pages/ExportReports'
import UserManagement from './pages/UserManagement'
import Sidebar from './components/layout/Sidebar'
import LeadDetail from './pages/LeadDetail'
import WelcomeModal from './components/WelcomeModal'

function App() {
  const [currentPage, setCurrentPage] = useState('login')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [selectedLeadId, setSelectedLeadId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [leadsCount, setLeadsCount] = useState(0)
  const [currentUser, setCurrentUser] = useState(null)
  const [showWelcome, setShowWelcome] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
    if (token) {
      setCurrentPage('dashboard')
      // Delay to ensure backend is ready
      setTimeout(() => {
        fetchLeadsCount()
        fetchCurrentUser()
      }, 500)
    }
  }, [])

  useEffect(() => {
    // Refresh count when page changes
    if (isLoggedIn && currentPage !== 'login' && currentPage !== 'landing') {
      fetchLeadsCount()
    }
  }, [currentPage])

  const fetchLeadsCount = async () => {
    try {
      const token = localStorage.getItem('token')
      // Use the API service function for consistency
      const response = await fetch(`http://${window.location.hostname}:8000/api/leads/?skip=0&limit=1&sort_by=created_at&sort_order=desc`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!response.ok) {
        console.error('Failed to fetch leads count:', response.status)
        return
      }

      const data = await response.json()
      console.log('Fetched leads count data:', data)
      const count = data.total || 0
      console.log('Setting leads count in sidebar to:', count)
      setLeadsCount(count)
    } catch (err) {
      console.error('Failed to fetch leads count:', err)
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://${window.location.hostname}:8000/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const userData = await response.json()
        setCurrentUser(userData)

        // Check if this is the first login (show welcome modal once)
        const hasSeenWelcome = localStorage.getItem(`welcome_shown_${userData.id}`)
        if (!hasSeenWelcome) {
          setShowWelcome(true)
        }
      }
    } catch (err) {
      console.error('Failed to fetch current user:', err)
    }
  }

  const handleCloseWelcome = () => {
    setShowWelcome(false)
    if (currentUser) {
      localStorage.setItem(`welcome_shown_${currentUser.id}`, 'true')
    }
  }

  const handleLoginSuccess = () => {
    setIsLoggedIn(true)
    setCurrentPage('dashboard')
    fetchLeadsCount()
    fetchCurrentUser()
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsLoggedIn(false)
    setCurrentPage('login')
  }

  const handleViewLead = (leadId) => {
    setSelectedLeadId(leadId)
    setCurrentPage('lead-detail')
  }

  if (selectedLeadId && currentPage === 'lead-detail') {
    return (
      <div className="flex h-screen bg-neutral-50 overflow-hidden">
        <Sidebar
          currentView={currentPage}
          onViewChange={setCurrentPage}
          onLogout={handleLogout}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          unreadCount={leadsCount}
          user={currentUser}
        />
        <div className="flex-1 overflow-auto w-full">
          <LeadDetail
            leadId={selectedLeadId}
            onBack={() => {
              setSelectedLeadId(null)
              setCurrentPage('leads')
            }}
            onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          />
        </div>
      </div>
    )
  }

  switch (currentPage) {
    case 'landing':
      return <Landing onGetStarted={() => setCurrentPage('login')} />

    case 'login':
      return <LoginV2
        onLoginSuccess={handleLoginSuccess}
        onNavigateToSignup={() => setCurrentPage('signup')}
      />

    case 'signup':
      return <Signup
        onNavigateToLogin={() => setCurrentPage('login')}
      />

    case 'analytics':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="analytics"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
            unreadCount={leadsCount}
          />
          <div className="flex-1 overflow-auto w-full">
            <AnalyticsEnterprise
              onBack={() => setCurrentPage('dashboard')}
              onLogout={handleLogout}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'leads':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="leads"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <Leads
              onViewLead={handleViewLead}
              onLogout={handleLogout}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'pipeline':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="pipeline"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <SalesPipeline
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'activities':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="activities"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <Activities
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'signals':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="signals"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <LiveSignals
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'search':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="search"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <SmartSearch
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'scoring':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="scoring"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <ScoreEngine
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'enrichment':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="enrichment"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <DataSources onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          </div>
        </div>
      )

    case 'notifications':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="notifications"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <Notifications
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'reports':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="reports"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <ExportReports
              onViewLead={handleViewLead}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
            />
          </div>
        </div>
      )

    case 'users':
      return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
          <Sidebar
            currentView="users"
            onViewChange={setCurrentPage}
            onLogout={handleLogout}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            user={currentUser}
          />
          <div className="flex-1 overflow-auto w-full">
            <UserManagement />
          </div>
        </div>
      )

    case 'dashboard':
    default:
      return (
        <>
          <DashboardPro
            onNavigate={setCurrentPage}
            onLogout={handleLogout}
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            currentUser={currentUser}
          />
          <AnimatePresence>
            {showWelcome && currentUser && (
              <WelcomeModal
                user={currentUser}
                onClose={handleCloseWelcome}
              />
            )}
          </AnimatePresence>
        </>
      )
  }
}

export default App
