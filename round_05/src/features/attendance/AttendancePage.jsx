import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const STATUS_COLORS = {
  Present:  'bg-green-100  text-green-800  dark:bg-green-900  dark:text-green-200',
  Absent:   'bg-red-100    text-red-800    dark:bg-red-900    dark:text-red-200',
  'Half Day':'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  'On Leave':'bg-blue-100   text-blue-800   dark:bg-blue-900   dark:text-blue-200',
};

const today = new Date().toISOString().split('T')[0];

const AttendancePage = () => {
  const [records, setRecords]     = useState([]);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [date, setDate]           = useState(today);
  const [filterStatus, setFilter] = useState('All');
  const [saving, setSaving]       = useState(null);  // id being saved

  const fetchAttendance = async (selectedDate) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/attendance', { params: { date: selectedDate } });
      setRecords(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to load attendance data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendance(date);
  }, [date]);

  const handleStatusChange = async (empId, newStatus) => {
    setSaving(empId);
    try {
      await api.post('/attendance', { employee_id: empId, date, status: newStatus });
      setRecords(prev =>
        prev.map(r => r.employee_id === empId ? { ...r, status: newStatus } : r)
      );
    } catch (err) {
      console.error(err);
      alert('Failed to update status. Please try again.');
    } finally {
      setSaving(null);
    }
  };

  const filtered = filterStatus === 'All'
    ? records
    : records.filter(r => r.status === filterStatus);

  const summary = ['Present', 'Absent', 'Half Day', 'On Leave'].map(s => ({
    label: s,
    count: records.filter(r => r.status === s).length,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Attendance</h2>
        <input
          type="date"
          value={date}
          max={today}
          onChange={e => setDate(e.target.value)}
          className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                     bg-white dark:bg-gray-700 text-gray-800 dark:text-white
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {summary.map(({ label, count }) => (
          <div
            key={label}
            onClick={() => setFilter(prev => prev === label ? 'All' : label)}
            className={`cursor-pointer rounded-xl p-4 shadow-sm border transition-all
              ${filterStatus === label
                ? 'border-blue-500 ring-2 ring-blue-300 dark:ring-blue-700'
                : 'border-gray-200 dark:border-gray-700'}
              bg-white dark:bg-gray-800`}
          >
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              {label}
            </p>
            <p className="text-3xl font-bold mt-1 text-gray-800 dark:text-white">{count}</p>
          </div>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
        {/* Filter pill */}
        {filterStatus !== 'All' && (
          <div className="px-6 pt-4 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            Filtered by:
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${STATUS_COLORS[filterStatus]}`}>
              {filterStatus}
            </span>
            <button onClick={() => setFilter('All')} className="ml-1 text-blue-500 hover:underline">
              Clear
            </button>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                {['#', 'Employee', 'Department', 'Status', 'Action'].map(h => (
                  <th key={h}
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan="5" className="px-6 py-10 text-center text-gray-400 dark:text-gray-500">
                    <span className="animate-pulse">Loading attendance…</span>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-10 text-center text-gray-400 dark:text-gray-500">
                    No records found.
                  </td>
                </tr>
              ) : (
                filtered.map((rec, idx) => (
                  <tr key={rec.employee_id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{idx + 1}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center font-semibold text-blue-700 dark:text-blue-300 text-sm flex-shrink-0">
                          {rec.first_name[0]}{rec.last_name[0]}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {rec.first_name} {rec.last_name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{rec.role}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">{rec.department}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 inline-flex text-xs font-semibold rounded-full ${STATUS_COLORS[rec.status] || 'bg-gray-100 text-gray-700'}`}>
                        {rec.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {['Present', 'Absent', 'Half Day', 'On Leave'].map(s => (
                          <button
                            key={s}
                            disabled={saving === rec.employee_id}
                            onClick={() => handleStatusChange(rec.employee_id, s)}
                            className={`text-xs px-2 py-1 rounded-md border transition-colors
                              ${rec.status === s
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-blue-400'}
                              disabled:opacity-50 disabled:cursor-not-allowed`}
                          >
                            {saving === rec.employee_id && rec.status !== s ? '…' : s}
                          </button>
                        ))}
                      </div>
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

export default AttendancePage;
