import React, { useState } from 'react'
import Login from './Login'
import Dashboard from './Dashboard'

export default function App() {
  const [token, setToken] = useState(null)

  return token ? <Dashboard token={token} onLogout={() => setToken(null)} /> : <Login onLogin={setToken} />
}
