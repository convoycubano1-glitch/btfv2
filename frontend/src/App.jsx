import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@clerk/react'
import { useEffect } from 'react'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Exchanges from './pages/Exchanges'
import Bots from './pages/Bots'
import Strategies from './pages/Strategies'
import Backtesting from './pages/Backtesting'
import Trading from './pages/Trading'
import Marketplace from './pages/Marketplace'
import Signals from './pages/Signals'
import Course from './pages/Course'
import Reports from './pages/Reports'
import Subscription from './pages/Subscription'
import AIAssistant from './pages/AIAssistant'
import Settings from './pages/Settings'
import Disclaimer from './components/common/Disclaimer'
import { PageLoader } from './components/common/LoadingSpinner'
import { setClerkGetToken } from './services/api'

// Syncs Clerk's getToken into the axios interceptor
function ClerkTokenSync() {
  const { getToken } = useAuth()
  useEffect(() => {
    setClerkGetToken(getToken)
  }, [getToken])
  return null
}

function ProtectedRoute({ children }) {
  const { isSignedIn, isLoaded } = useAuth()
  if (!isLoaded) return <PageLoader />
  if (!isSignedIn) return <Navigate to="/login" replace />
  return children
}

function PublicRoute({ children }) {
  const { isSignedIn, isLoaded } = useAuth()
  if (!isLoaded) return <PageLoader />
  if (isSignedIn) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <ClerkTokenSync />
      <Disclaimer />
      <Routes>
        {/* Public */}
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Protected — wrapped in sidebar layout */}
        <Route
          path="/"
          element={<ProtectedRoute><Layout /></ProtectedRoute>}
        >
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="exchanges" element={<Exchanges />} />
          <Route path="bots" element={<Bots />} />
          <Route path="strategies" element={<Strategies />} />
          <Route path="backtesting" element={<Backtesting />} />
          <Route path="trading" element={<Trading />} />
          <Route path="marketplace" element={<Marketplace />} />
          <Route path="signals" element={<Signals />} />
          <Route path="course" element={<Course />} />
          <Route path="reports" element={<Reports />} />
          <Route path="subscription" element={<Subscription />} />
          <Route path="ai" element={<AIAssistant />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
