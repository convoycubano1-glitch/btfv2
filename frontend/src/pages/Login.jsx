import { SignIn } from '@clerk/react'
import { Zap } from 'lucide-react'

export default function Login() {
  return (
    <div className="min-h-screen bg-hero-gradient flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-brand-500 rounded-2xl mb-4 shadow-lg shadow-brand-500/30">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">TradeBotHub Pro</h1>
          <p className="text-gray-400 mt-1 text-sm">Professional Algorithmic Trading</p>
        </div>

        <SignIn
          afterSignInUrl="/dashboard"
          signUpUrl="/register"
          appearance={{
            variables: {
              colorPrimary: '#6366f1',
              colorBackground: '#1a1d27',
              colorInputBackground: '#0f1117',
              colorText: '#e5e7eb',
              colorTextSecondary: '#9ca3af',
              colorInputText: '#e5e7eb',
              borderRadius: '0.75rem',
            },
            elements: {
              card: 'shadow-none bg-transparent',
              formButtonPrimary: 'btn-primary',
            },
          }}
        />

        <p className="text-center text-xs text-gray-600 mt-6">
          ⚠️ Trading involves substantial risk of loss. Paper trade first.
        </p>
      </div>
    </div>
  )
}
