import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { Toaster } from 'react-hot-toast'
import { ClerkProvider } from '@clerk/react'
import App from './App.jsx'
import { store } from './store/index.js'
import './index.css'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY} afterSignOutUrl="/login">
      <Provider store={store}>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#1a1d27',
              color: '#e5e7eb',
              border: '1px solid #2a2d3a',
            },
            success: { iconTheme: { primary: '#00d395', secondary: '#0f1117' } },
            error: { iconTheme: { primary: '#ff4d4f', secondary: '#0f1117' } },
          }}
        />
      </Provider>
    </ClerkProvider>
  </React.StrictMode>
)
