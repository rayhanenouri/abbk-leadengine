import { useState, useEffect } from 'react'
import Landing from './pages/Landing'
import LoginV2 from './pages/LoginV2'
import DashboardV2 from './pages/DashboardV2'
import Analytics from './pages/Analytics'

function App() {
  const [currentPage, setCurrentPage] = useState('landing') // 'landing', 'login', 'dashboard', 'analytics'
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    // Check if user has a token
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)

    // If user is logged in, show dashboard instead of landing
    if (token && currentPage === 'landing') {
      setCurrentPage('dashboard')
    }
  }, [])

  const handleLoginSuccess = () => {
    setIsLoggedIn(true)
    setCurrentPage('dashboard')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsLoggedIn(false)
    setCurrentPage('landing')
  }

  // Route to different pages
  switch (currentPage) {
    case 'landing':
      return <Landing onGetStarted={() => setCurrentPage('login')} />

    case 'login':
      return <LoginV2 onLoginSuccess={handleLoginSuccess} />

    case 'analytics':
      return <Analytics onBack={() => setCurrentPage('dashboard')} onLogout={handleLogout} />

    case 'dashboard':
    default:
      return (
        <DashboardV2
          onNavigateToAnalytics={() => setCurrentPage('analytics')}
          onLogout={handleLogout}
        />
      )
  }
}

export default App
