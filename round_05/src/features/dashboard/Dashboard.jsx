import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    presentToday: 0,
    absentToday: 0,
    pendingLeaves: 0
  });
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const today = new Date().toISOString().split('T')[0];
        
        // Fetch all data concurrently
        const [empRes, attRes, leavesRes] = await Promise.all([
          api.get('/employees?limit=100'),
          api.get('/attendance', { params: { date: today } }),
          api.get('/leaves')
        ]);
        
        const employees = empRes.data.data || empRes.data || [];
        const attendance = attRes.data || [];
        const leaves = leavesRes.data || [];
        
        const present = attendance.filter(a => a.status === 'Present').length;
        const absent = attendance.filter(a => a.status === 'Absent' || a.status === 'On Leave').length;
        const pending = leaves.filter(l => l.status === 'Pending').length;
        
        setStats({
          totalEmployees: employees.length,
          presentToday: present,
          absentToday: absent,
          pendingLeaves: pending
        });
      } catch (err) {
        console.error("Failed to load dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  const statCards = [
    { title: 'Total Employees', value: stats.totalEmployees, icon: '👥', color: 'bg-blue-500', link: '/employees' },
    { title: 'Present Today', value: stats.presentToday, icon: '✅', color: 'bg-green-500', link: '/attendance' },
    { title: 'Absent/Leave Today', value: stats.absentToday, icon: '❌', color: 'bg-red-500', link: '/attendance' },
    { title: 'Pending Leaves', value: stats.pendingLeaves, icon: '⏳', color: 'bg-yellow-500', link: '/leaves' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Dashboard Overview</h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Welcome back to ERP Pro. Here's what's happening today.</p>
        </div>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 animate-pulse h-32"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card, idx) => (
            <Link key={idx} to={card.link} className="block group">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-all duration-200 transform group-hover:-translate-y-1">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{card.title}</p>
                    <h3 className="text-3xl font-bold text-gray-800 dark:text-white">{card.value}</h3>
                  </div>
                  <div className={`${card.color} w-12 h-12 rounded-lg flex items-center justify-center text-white text-2xl shadow-sm`}>
                    {card.icon}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        {/* Quick Actions */}
        <div className="lg:col-span-1 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link to="/employees" className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <span className="mr-3 text-lg">➕</span> Add New Employee
            </Link>
            <Link to="/attendance" className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <span className="mr-3 text-lg">📝</span> Mark Attendance
            </Link>
            <Link to="/leaves" className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <span className="mr-3 text-lg">📬</span> Review Leaves
            </Link>
            <Link to="/settings" className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <span className="mr-3 text-lg">⚙️</span> System Settings
            </Link>
          </div>
        </div>

        {/* System Activity Placeholder */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Recent Activity</h3>
            <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">View All</button>
          </div>
          
          <div className="space-y-4">
            {[
              { text: 'Leave request approved for Neha Desai', time: '10 mins ago', icon: '✅', color: 'bg-green-100 text-green-600' },
              { text: 'Attendance marked for Engineering Dept', time: '1 hour ago', icon: '📅', color: 'bg-blue-100 text-blue-600' },
              { text: 'New employee Ankit Mehta added', time: '3 hours ago', icon: '👤', color: 'bg-purple-100 text-purple-600' },
              { text: 'Leave request rejected for Karan Malhotra', time: 'Yesterday', icon: '❌', color: 'bg-red-100 text-red-600' }
            ].map((activity, idx) => (
              <div key={idx} className="flex items-start p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0">
                <div className={`${activity.color} w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5`}>
                  <span className="text-sm">{activity.icon}</span>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{activity.text}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
