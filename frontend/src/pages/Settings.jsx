import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function Settings() {
  const { user, signOut } = useAuth()
  const [form, setForm] = useState({ full_name: '', username: '' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) setForm({ full_name: user.full_name || '', username: user.username || '' })
  }, [user])

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.patch('/auth/me', form)
      toast.success('Profile updated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Settings</h2>
        <p className="text-sm text-gray-400 mt-1">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <div className="card">
        <h3 className="font-semibold text-white mb-4">Profile</h3>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input className="input opacity-60 cursor-not-allowed" value={user?.email || ''} disabled />
          </div>
          <div>
            <label className="label">Username</label>
            <input className="input" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </div>
          <div>
            <label className="label">Full Name</label>
            <input className="input" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Optional" />
          </div>
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      {/* Account info */}
      <div className="card">
        <h3 className="font-semibold text-white mb-4">Account</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Plan</span>
            <span className="text-white capitalize font-semibold">{user?.subscription?.plan || 'Free'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Role</span>
            <span className="text-white capitalize">{user?.role}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Account Status</span>
            <span className={user?.is_active ? 'text-trading-green' : 'text-trading-red'}>
              {user?.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="card">
        <h3 className="font-semibold text-white mb-4">Security</h3>
        <div className="space-y-3 text-sm text-gray-400">
          <p>• API keys are encrypted with AES-256 (Fernet) before storage</p>
          <p>• Withdrawal permissions are permanently disabled on all exchange connections</p>
          <p>• JWT tokens expire after 30 minutes; refresh tokens after 7 days</p>
          <p>• Emergency stop can pause all bots instantly from the header</p>
        </div>
      </div>

      {/* Danger zone */}
      <div className="card border-trading-red/30">
        <h3 className="font-semibold text-trading-red mb-4">Danger Zone</h3>
        <button onClick={signOut} className="btn-danger flex items-center gap-2">
          Sign Out
        </button>
      </div>
    </div>
  )
}
