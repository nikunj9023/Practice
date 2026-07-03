import React, { useEffect, useState } from 'react'
import Employees from './Employees'
import ERP from './ERP'

const cardData = [
  { title: 'Revenue', value: '$24k', change: '+12%' },
  { title: 'Users', value: '1.2k', change: '+8%' },
  { title: 'Orders', value: '320', change: '+5%' },
]

const transactions = [
  { id: 1, client: 'Ava', amount: '$480', status: 'Paid' },
  { id: 2, client: 'Noah', amount: '$230', status: 'Pending' },
  { id: 3, client: 'Mia', amount: '$890', status: 'Paid' },
]

export default function Dashboard({ token, onLogout }) {
  const [info, setInfo] = useState(null)
  const [error, setError] = useState(null)
  const [darkMode, setDarkMode] = useState(true)
  const [view, setView] = useState('charts')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        })
        const data = await res.json()
        if (res.ok) setInfo(data)
        else setError(data.message || 'Failed')
      } catch (err) {
        setError(err.message)
      }
    }
    fetchData()
  }, [token])

  if (error) return <div style={{ padding: 20 }}>Error: {error}</div>
  if (!info) return <div style={{ padding: 20 }}>Loading...</div>

  const theme = darkMode
    ? {
        bg: '#0f172a',
        panel: '#111827',
        text: '#f9fafb',
        muted: '#94a3b8',
        border: '#334155',
        accent: '#38bdf8',
      }
    : {
        bg: '#f8fafc',
        panel: '#ffffff',
        text: '#0f172a',
        muted: '#64748b',
        border: '#e2e8f0',
        accent: '#2563eb',
      }

  return (
    <div style={{ minHeight: '100vh', background: theme.bg, color: theme.text, display: 'flex', fontFamily: 'Arial, sans-serif' }}>
      <aside style={{ width: 240, background: theme.panel, borderRight: `1px solid ${theme.border}`, padding: 20 }}>
        <h3 style={{ marginTop: 0 }}>Admin Panel</h3>
        <nav style={{ display: 'grid', gap: 10, marginTop: 20 }}>
          <div style={{ padding: '10px 12px', borderRadius: 8, background: theme.accent, color: '#fff' }}>Dashboard</div>
          <button onClick={() => setView('charts')} style={{ padding: '10px 12px', borderRadius: 8, color: theme.text, background: 'transparent', border: `1px solid ${theme.border}`, cursor: 'pointer' }}>Charts</button>
          <button onClick={() => setView('table')} style={{ padding: '10px 12px', borderRadius: 8, color: theme.text, background: 'transparent', border: `1px solid ${theme.border}`, cursor: 'pointer' }}>Tables</button>
          <button onClick={() => setView('erp')} style={{ padding: '10px 12px', borderRadius: 8, color: theme.text, background: 'transparent', border: `1px solid ${theme.border}`, cursor: 'pointer' }}>ERP</button>
          <button onClick={() => setView('employees')} style={{ padding: '10px 12px', borderRadius: 8, color: theme.text, background: 'transparent', border: `1px solid ${theme.border}`, cursor: 'pointer' }}>Employees</button>
        </nav>
        <button onClick={onLogout} style={{ marginTop: 30, width: '100%', padding: '10px 12px', border: 'none', borderRadius: 8, background: '#ef4444', color: '#fff', cursor: 'pointer' }}>Logout</button>
      </aside>

      <main style={{ flex: 1, padding: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h2 style={{ margin: 0 }}>{info.message}</h2>
            <p style={{ margin: '6px 0 0', color: theme.muted }}>Welcome back, {info.user?.username || 'User'}</p>
          </div>
          <button onClick={() => setDarkMode(!darkMode)} style={{ padding: '8px 12px', borderRadius: 8, border: `1px solid ${theme.border}`, background: theme.panel, color: theme.text, cursor: 'pointer' }}>
            {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 20 }}>
          {cardData.map((card) => (
            <div key={card.title} style={{ background: theme.panel, border: `1px solid ${theme.border}`, borderRadius: 12, padding: 16 }}>
              <div style={{ color: theme.muted, fontSize: 14 }}>{card.title}</div>
              <div style={{ fontSize: 26, fontWeight: 700, marginTop: 8 }}>{card.value}</div>
              <div style={{ color: theme.accent, marginTop: 6, fontSize: 13 }}>{card.change} this month</div>
            </div>
          ))}
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 20 }}>
          <div style={{ background: theme.panel, border: `1px solid ${theme.border}`, borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ marginTop: 0 }}>{view === 'charts' ? 'Charts' : 'Table'}</h3>
              <div>
                <button onClick={() => setView('charts')} style={{ marginRight: 8, padding: '6px 10px', borderRadius: 8, border: `1px solid ${theme.border}`, background: view === 'charts' ? theme.accent : 'transparent', color: view === 'charts' ? '#fff' : theme.text }}>Charts</button>
                <button onClick={() => setView('table')} style={{ padding: '6px 10px', borderRadius: 8, border: `1px solid ${theme.border}`, background: view === 'table' ? theme.accent : 'transparent', color: view === 'table' ? '#fff' : theme.text }}>Table</button>
              </div>
            </div>

            {view === 'charts' ? (
              <div style={{ display: 'flex', alignItems: 'flex-end', height: 160, gap: 12, marginTop: 12 }}>
                {[45, 70, 55, 85, 65, 90].map((height, index) => (
                  <div key={index} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: '100%', height: height, borderRadius: 8, background: `linear-gradient(180deg, ${theme.accent}, #60a5fa)` }} />
                    <span style={{ color: theme.muted, fontSize: 12 }}>W{index + 1}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ marginTop: 12 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ textAlign: 'left', color: theme.muted }}>
                      <th style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>Client</th>
                      <th style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>Amount</th>
                      <th style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((row) => (
                      <tr key={row.id}>
                        <td style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>{row.client}</td>
                        <td style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>{row.amount}</td>
                        <td style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>
                          <span style={{ padding: '4px 8px', borderRadius: 999, background: row.status === 'Paid' ? '#16a34a22' : '#f59e0b22', color: row.status === 'Paid' ? '#22c55e' : '#f59e0b' }}>{row.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div style={{ background: theme.panel, border: `1px solid ${theme.border}`, borderRadius: 12, padding: 16 }}>
            <h3 style={{ marginTop: 0 }}>Quick Notes</h3>
            <ul style={{ color: theme.muted, lineHeight: 1.6 }}>
              <li>Weekly report ready</li>
              <li>2 pending approvals</li>
              <li>New feedback received</li>
            </ul>
          </div>
        </section>

        {view === 'erp' ? (
          <ERP token={token} />
        ) : view === 'employees' ? (
          <section style={{ background: theme.panel, border: `1px solid ${theme.border}`, borderRadius: 12, padding: 16 }}>
            <Employees token={token} />
          </section>
        ) : (
          <section style={{ background: theme.panel, border: `1px solid ${theme.border}`, borderRadius: 12, padding: 16 }}>
            <h3 style={{ marginTop: 0 }}>Tables</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: theme.muted }}>
                  <th style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>Client</th>
                  <th style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>Amount</th>
                  <th style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((row) => (
                  <tr key={row.id}>
                    <td style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>{row.client}</td>
                    <td style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>{row.amount}</td>
                    <td style={{ padding: '10px 8px', borderBottom: `1px solid ${theme.border}` }}>
                      <span style={{ padding: '4px 8px', borderRadius: 999, background: row.status === 'Paid' ? '#16a34a22' : '#f59e0b22', color: row.status === 'Paid' ? '#22c55e' : '#f59e0b' }}>{row.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  )
}
