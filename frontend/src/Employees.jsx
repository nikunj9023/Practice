import React, { useEffect, useState, useRef } from 'react'

export default function Employees({ token }) {
  const [employees, setEmployees] = useState([])
  const [page, setPage] = useState(1)
  const [perPage] = useState(5)
  const [total, setTotal] = useState(0)
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [position, setPosition] = useState('')
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)

  const [editing, setEditing] = useState(null)
  const [editPreview, setEditPreview] = useState(null)

  const imageInputRef = useRef()

  const load = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/employees?q=${encodeURIComponent(q)}&page=${page}&per_page=${perPage}`, { headers: { Authorization: `Bearer ${token}` } })
      const data = await res.json()
      if (res.ok) {
        setEmployees(data.items)
        setTotal(data.total)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page, q])

  useEffect(() => {
    if (!image) { setImagePreview(null); return }
    const url = URL.createObjectURL(image)
    setImagePreview(url)
    return () => URL.revokeObjectURL(url)
  }, [image])

  useEffect(() => {
    if (!editPreview) return
    return () => {
      try { URL.revokeObjectURL(editPreview) } catch(e){}
    }
  }, [editPreview])

  const handleCreate = async (e) => {
    e.preventDefault()
    const fd = new FormData()
    fd.append('name', name)
    fd.append('email', email)
    fd.append('position', position)
    if (image) fd.append('image', image)

    const res = await fetch('/api/employees', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
    const data = await res.json()
    if (res.ok) {
      setName('')
      setEmail('')
      setPosition('')
      setImage(null)
      setImagePreview(null)
      setPage(1)
      load()
    } else {
      alert(data.message || 'Failed')
    }
  }

  const openEdit = (emp) => {
    setEditing(emp)
    setEditPreview(emp.image || null)
    setTimeout(()=>{ if(imageInputRef.current) imageInputRef.current.value = '' }, 0)
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    if (!editing) return
    const fd = new FormData()
    fd.append('name', editing.name)
    fd.append('email', editing.email)
    fd.append('position', editing.position)
    if (editing._newImage) fd.append('image', editing._newImage)

    const res = await fetch(`/api/employees/${editing.id}`, { method: 'PUT', headers: { Authorization: `Bearer ${token}` }, body: fd })
    const data = await res.json()
    if (res.ok) {
      setEditing(null)
      setEditPreview(null)
      load()
    } else alert(data.message || 'Update failed')
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this employee?')) return
    const res = await fetch(`/api/employees/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) load()
    else alert('Delete failed')
  }

  const pages = Math.max(1, Math.ceil(total / perPage))

  return (
    <div>
      <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
        <input placeholder="Search" value={q} onChange={e=>setQ(e.target.value)} />
        <button onClick={()=>{ setPage(1); load(); }}>Search</button>
      </div>

      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ flex: 1 }}>
          <h4>Employees</h4>
          {loading ? <div>Loading...</div> : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: 8 }}>Name</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Email</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Position</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Image</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map(emp => (
                  <tr key={emp.id}>
                    <td style={{ padding: 8 }}>{emp.name}</td>
                    <td style={{ padding: 8 }}>{emp.email}</td>
                    <td style={{ padding: 8 }}>{emp.position}</td>
                    <td style={{ padding: 8 }}>{emp.image ? <img src={emp.image} alt="" style={{ height: 40 }} /> : '-'}</td>
                    <td style={{ padding: 8 }}>
                      <button onClick={()=>openEdit(emp)} style={{ marginRight: 8 }}>Edit</button>
                      <button onClick={()=>handleDelete(emp.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div style={{ marginTop: 12 }}>
            <button onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page<=1}>Prev</button>
            <span style={{ margin: '0 8px' }}>{page} / {pages}</span>
            <button onClick={()=>setPage(p=>Math.min(pages,p+1))} disabled={page>=pages}>Next</button>
          </div>
        </div>

        <aside style={{ width: 320 }}>
          <h4>{editing ? 'Edit Employee' : 'Add Employee'}</h4>
          <form onSubmit={editing ? handleUpdate : handleCreate}>
            <div style={{ marginBottom: 8 }}>
              <input placeholder="Name" value={editing ? editing.name : name} onChange={e=> editing ? setEditing({...editing, name: e.target.value}) : setName(e.target.value)} style={{ width: '100%' }} />
            </div>
            <div style={{ marginBottom: 8 }}>
              <input placeholder="Email" value={editing ? editing.email : email} onChange={e=> editing ? setEditing({...editing, email: e.target.value}) : setEmail(e.target.value)} style={{ width: '100%' }} />
            </div>
            <div style={{ marginBottom: 8 }}>
              <input placeholder="Position" value={editing ? editing.position : position} onChange={e=> editing ? setEditing({...editing, position: e.target.value}) : setPosition(e.target.value)} style={{ width: '100%' }} />
            </div>
            <div style={{ marginBottom: 8 }}>
              <input ref={imageInputRef} type="file" onChange={e=>{
                const f = e.target.files[0]
                if (editing) {
                  setEditing({...editing, _newImage: f})
                  if (f) setEditPreview(URL.createObjectURL(f))
                } else {
                  setImage(f)
                }
              }} />
            </div>
            <div style={{ marginBottom: 8 }}>
              {editing ? (editPreview ? <img src={editPreview} alt="preview" style={{ height: 80 }} /> : 'No image') : (imagePreview ? <img src={imagePreview} alt="preview" style={{ height: 80 }} /> : 'No image')}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="submit">{editing ? 'Save' : 'Create'}</button>
              {editing && <button type="button" onClick={()=>{ setEditing(null); setEditPreview(null); }}>Cancel</button>}
            </div>
          </form>
        </aside>
      </div>
    </div>
  )
}
