import React, { useEffect, useState } from 'react'

export default function ERP({ token }) {
  const [tenants, setTenants] = useState([])
  const [tenantId, setTenantId] = useState('')
  const [metrics, setMetrics] = useState(null)
  const [customers, setCustomers] = useState([])
  const [invoices, setInvoices] = useState([])
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [customerEmail, setCustomerEmail] = useState('')
  const [invoiceNumber, setInvoiceNumber] = useState('')
  const [amount, setAmount] = useState('')

  const authHeaders = { Authorization: `Bearer ${token}` }

  const loadTenants = async () => {
    const res = await fetch('/api/tenants', { headers: authHeaders })
    const data = await res.json()
    if (res.ok) {
      setTenants(data.items)
      if (!tenantId && data.items[0]) {
        setTenantId(data.items[0].id)
      }
    }
  }

  const loadData = async (selectedTenantId = tenantId) => {
    if (!selectedTenantId) return
    const [metricsRes, customersRes, invoicesRes] = await Promise.all([
      fetch(`/api/erp/dashboard?tenant_id=${selectedTenantId}`, { headers: authHeaders }),
      fetch(`/api/customers?tenant_id=${selectedTenantId}`, { headers: authHeaders }),
      fetch(`/api/invoices?tenant_id=${selectedTenantId}`, { headers: authHeaders }),
    ])
    const metricsData = await metricsRes.json()
    const customersData = await customersRes.json()
    const invoicesData = await invoicesRes.json()
    if (metricsRes.ok) setMetrics(metricsData)
    if (customersRes.ok) setCustomers(customersData.items || [])
    if (invoicesRes.ok) setInvoices(invoicesData.items || [])
  }

  useEffect(() => { loadTenants() }, [])
  useEffect(() => { loadData(tenantId) }, [tenantId])

  const createTenant = async (e) => {
    e.preventDefault()
    const res = await fetch('/api/tenants', { method: 'POST', headers: { ...authHeaders, 'Content-Type': 'application/json' }, body: JSON.stringify({ name, slug }) })
    if (res.ok) {
      setName('')
      setSlug('')
      loadTenants()
    }
  }

  const createCustomer = async (e) => {
    e.preventDefault()
    const res = await fetch('/api/customers', { method: 'POST', headers: { ...authHeaders, 'Content-Type': 'application/json' }, body: JSON.stringify({ tenant_id: tenantId, name: customerName, email: customerEmail }) })
    if (res.ok) {
      setCustomerName('')
      setCustomerEmail('')
      loadData(tenantId)
    }
  }

  const createInvoice = async (e) => {
    e.preventDefault()
    const res = await fetch('/api/invoices', { method: 'POST', headers: { ...authHeaders, 'Content-Type': 'application/json' }, body: JSON.stringify({ tenant_id: tenantId, invoice_number: invoiceNumber, customer_id: customers[0]?.id || 1, amount }) })
    if (res.ok) {
      setInvoiceNumber('')
      setAmount('')
      loadData(tenantId)
    }
  }

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div style={{ display: 'grid', gap: 12 }}>
        <label>
          Tenant
          <select value={tenantId} onChange={(e) => setTenantId(e.target.value)} style={{ width: '100%', marginTop: 6, padding: 8 }}>
            {tenants.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
        </label>

        <form onSubmit={createTenant} style={{ display: 'flex', gap: 8 }}>
          <input placeholder="Tenant name" value={name} onChange={(e) => setName(e.target.value)} />
          <input placeholder="Slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
          <button type="submit">Add Tenant</button>
        </form>
      </div>

      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          <div style={{ padding: 16, border: '1px solid #e2e8f0', borderRadius: 8 }}><strong>Customers</strong><div>{metrics.metrics.customers}</div></div>
          <div style={{ padding: 16, border: '1px solid #e2e8f0', borderRadius: 8 }}><strong>Invoices</strong><div>{metrics.metrics.invoices}</div></div>
          <div style={{ padding: 16, border: '1px solid #e2e8f0', borderRadius: 8 }}><strong>Revenue</strong><div>${Number(metrics.metrics.revenue || 0).toFixed(2)}</div></div>
          <div style={{ padding: 16, border: '1px solid #e2e8f0', borderRadius: 8 }}><strong>Outstanding</strong><div>${Number(metrics.metrics.outstanding || 0).toFixed(2)}</div></div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <h4>Customers</h4>
          <form onSubmit={createCustomer} style={{ display: 'grid', gap: 8, marginBottom: 8 }}>
            <input placeholder="Customer name" value={customerName} onChange={(e) => setCustomerName(e.target.value)} />
            <input placeholder="Customer email" value={customerEmail} onChange={(e) => setCustomerEmail(e.target.value)} />
            <button type="submit">Add Customer</button>
          </form>
          <ul>
            {customers.map((c) => <li key={c.id}>{c.name} — {c.email || 'No email'}</li>)}
          </ul>
        </div>

        <div>
          <h4>Invoices</h4>
          <form onSubmit={createInvoice} style={{ display: 'grid', gap: 8, marginBottom: 8 }}>
            <input placeholder="Invoice number" value={invoiceNumber} onChange={(e) => setInvoiceNumber(e.target.value)} />
            <input placeholder="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
            <button type="submit">Add Invoice</button>
          </form>
          <ul>
            {invoices.map((invoice) => <li key={invoice.id}>{invoice.invoice_number} — ${Number(invoice.amount).toFixed(2)} ({invoice.status})</li>)}
          </ul>
        </div>
      </div>
    </div>
  )
}
