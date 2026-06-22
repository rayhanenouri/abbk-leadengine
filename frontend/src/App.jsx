import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentView, setCurrentView] = useState('dashboard')

  useEffect(() => {
    // Check if user has a token
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
  }, [])

  const handleLoginSuccess = () => {
    setIsLoggedIn(true)
  }

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  if (currentView === 'analytics') {
    return <Analytics onBack={() => setCurrentView('dashboard')} />
  }

  return <Dashboard onNavigateToAnalytics={() => setCurrentView('analytics')} />
}

export default App
