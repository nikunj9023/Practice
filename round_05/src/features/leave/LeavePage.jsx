import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const STATUS_STYLES = {
  Pending:  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  Approved: 'bg-green-100  text-green-800  dark:bg-green-900  dark:text-green-200',
  Rejected: 'bg-red-100    text-red-800    dark:bg-red-900    dark:text-red-200',
};

const LEAVE_TYPES = ['Sick Leave', 'Casual Leave', 'Earned Leave', 'Maternity Leave', 'Unpaid Leave'];

const EMPTY_FORM = {
  employee_id: '',
  leave_type: LEAVE_TYPES[0],
  from_date: '',
  to_date: '',
  reason: '',
};

const LeavePage = () => {
  const [leaves, setLeaves]           = useState([]);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState(null);
  const [filterStatus, setFilter]     = useState('All');
  const [showForm, setShowForm]       = useState(false);
  const [form, setForm]               = useState(EMPTY_FORM);
  const [submitting, setSubmitting]   = useState(false);
  const [actionId, setActionId]       = useState(null);   // id being approved/rejected

  const fetchLeaves = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/leaves');
      setLeaves(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to load leave requests. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLeaves(); }, []);

  /* ── Apply Leave ─────────────────────────────────── */
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.employee_id || !form.from_date || !form.to_date) {
      alert('Please fill all required fields.');
      return;
    }
    setSubmitting(true);
    try {
      const res = await api.post('/leaves', form);
      setLeaves(prev => [res.data, ...prev]);
      setForm(EMPTY_FORM);
      setShowForm(false);
    } catch (err) {
      console.error(err);
      alert('Failed to submit leave request.');
    } finally {
      setSubmitting(false);
    }
  };

  /* ── Approve / Reject ────────────────────────────── */
  const handleAction = async (id, status) => {
    setActionId(id);
    try {
      await api.patch(`/leaves/${id}`, { status });
      setLeaves(prev => prev.map(l => l.id === id ? { ...l, status } : l));
    } catch (err) {
      console.error(err);
      alert(`Failed to ${status.toLowerCase()} leave request.`);
    } finally {
      setActionId(null);
    }
  };

  /* ── Helpers ─────────────────────────────────────── */
  const filtered = filterStatus === 'All' ? leaves : leaves.filter(l => l.status === filterStatus);

  const summary = ['Pending', 'Approved', 'Rejected'].map(s => ({
    label: s,
    count: leaves.filter(l => l.status === s).length,
  }));

  const daysBetween = (from, to) => {
    const d1 = new Date(from), d2 = new Date(to);
    return Math.max(1, Math.round((d2 - d1) / 86400000) + 1);
  };

  return (
    <div className="space-y-6">

      {/* ── Header ─────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Leave Requests</h2>
        <button
          onClick={() => setShowForm(prev => !prev)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors shadow"
        >
          {showForm ? '✕  Close Form' : '＋  Apply for Leave'}
        </button>
      </div>

      {/* ── Apply Form ─────────────────────────────── */}
      {showForm && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 border border-blue-200 dark:border-blue-700">
          <h3 className="text-lg font-semibold text-gray-700 dark:text-white mb-4">New Leave Request</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">

            {/* Employee ID */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Employee ID <span className="text-red-500">*</span>
              </label>
              <input
                type="number" min="1" max="12" required
                value={form.employee_id}
                onChange={e => setForm(f => ({ ...f, employee_id: e.target.value }))}
                placeholder="e.g. 1"
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                           bg-white dark:bg-gray-700 text-gray-800 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Leave Type */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Leave Type</label>
              <select
                value={form.leave_type}
                onChange={e => setForm(f => ({ ...f, leave_type: e.target.value }))}
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                           bg-white dark:bg-gray-700 text-gray-800 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {LEAVE_TYPES.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>

            {/* From Date */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                From Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date" required
                value={form.from_date}
                onChange={e => setForm(f => ({ ...f, from_date: e.target.value }))}
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                           bg-white dark:bg-gray-700 text-gray-800 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* To Date */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                To Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date" required
                value={form.to_date}
                min={form.from_date}
                onChange={e => setForm(f => ({ ...f, to_date: e.target.value }))}
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                           bg-white dark:bg-gray-700 text-gray-800 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Reason */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Reason</label>
              <textarea
                rows={3}
                value={form.reason}
                onChange={e => setForm(f => ({ ...f, reason: e.target.value }))}
                placeholder="Brief reason for leave…"
                className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                           bg-white dark:bg-gray-700 text-gray-800 dark:text-white
                           focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>

            {/* Submit */}
            <div className="sm:col-span-2 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => { setShowForm(false); setForm(EMPTY_FORM); }}
                className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                type="submit" disabled={submitting}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg transition-colors"
              >
                {submitting ? 'Submitting…' : 'Submit Request'}
              </button>
            </div>

          </form>
        </div>
      )}

      {/* ── Summary Cards ──────────────────────────── */}
      <div className="grid grid-cols-3 gap-4">
        {summary.map(({ label, count }) => (
          <div
            key={label}
            onClick={() => setFilter(prev => prev === label ? 'All' : label)}
            className={`cursor-pointer rounded-xl p-4 shadow-sm border transition-all
              ${filterStatus === label ? 'border-blue-500 ring-2 ring-blue-300 dark:ring-blue-700' : 'border-gray-200 dark:border-gray-700'}
              bg-white dark:bg-gray-800`}
          >
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{label}</p>
            <p className="text-3xl font-bold mt-1 text-gray-800 dark:text-white">{count}</p>
          </div>
        ))}
      </div>

      {/* ── Error ──────────────────────────────────── */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">{error}</div>
      )}

      {/* ── Table ──────────────────────────────────── */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">

        {filterStatus !== 'All' && (
          <div className="px-6 pt-4 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            Filtered by:
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${STATUS_STYLES[filterStatus]}`}>
              {filterStatus}
            </span>
            <button onClick={() => setFilter('All')} className="ml-1 text-blue-500 hover:underline">Clear</button>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                {['Employee', 'Leave Type', 'Duration', 'Days', 'Reason', 'Status', 'Actions'].map(h => (
                  <th key={h} scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-10 text-center text-gray-400 dark:text-gray-500">
                    <span className="animate-pulse">Loading leave requests…</span>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-10 text-center text-gray-400 dark:text-gray-500">
                    No leave requests found.
                  </td>
                </tr>
              ) : (
                filtered.map(leave => (
                  <tr key={leave.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">

                    {/* Employee */}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center font-semibold text-purple-700 dark:text-purple-300 text-sm flex-shrink-0">
                          {leave.first_name?.[0]}{leave.last_name?.[0]}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {leave.first_name} {leave.last_name}
                          </p>
                          <p className="text-xs text-gray-400">{leave.department}</p>
                        </div>
                      </div>
                    </td>

                    {/* Leave Type */}
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                      {leave.leave_type}
                    </td>

                    {/* Duration */}
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                      {leave.from_date} → {leave.to_date}
                    </td>

                    {/* Days */}
                    <td className="px-6 py-4 text-sm font-semibold text-gray-800 dark:text-white text-center">
                      {daysBetween(leave.from_date, leave.to_date)}
                    </td>

                    {/* Reason */}
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                      {leave.reason || '—'}
                    </td>

                    {/* Status Badge */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-1 inline-flex text-xs font-semibold rounded-full ${STATUS_STYLES[leave.status]}`}>
                        {leave.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      {leave.status === 'Pending' ? (
                        <div className="flex gap-2">
                          <button
                            disabled={actionId === leave.id}
                            onClick={() => handleAction(leave.id, 'Approved')}
                            className="px-3 py-1 text-xs font-semibold bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors disabled:opacity-50"
                          >
                            {actionId === leave.id ? '…' : '✓ Approve'}
                          </button>
                          <button
                            disabled={actionId === leave.id}
                            onClick={() => handleAction(leave.id, 'Rejected')}
                            className="px-3 py-1 text-xs font-semibold bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors disabled:opacity-50"
                          >
                            {actionId === leave.id ? '…' : '✕ Reject'}
                          </button>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400 italic">No action</span>
                      )}
                    </td>

                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LeavePage;
