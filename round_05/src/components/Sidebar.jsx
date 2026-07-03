import React from 'react';
import { NavLink } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logout } from '../features/auth/authSlice';

const Sidebar = ({ isCollapsed, toggleSidebar }) => {
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(logout());
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: '📊' },
    { name: 'Employees', path: '/employees', icon: '👥' },
    { name: 'Attendance', path: '/attendance', icon: '📅' },
    { name: 'Leave Requests', path: '/leaves', icon: '✈️' },
    { name: 'Settings', path: '/settings', icon: '⚙️' },
  ];

  return (
    <aside 
      className={`fixed top-0 left-0 h-screen transition-all duration-300 z-40 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
      ${isCollapsed ? 'w-20' : 'w-64'} `}
    >
      <div className="flex flex-col h-full">
        {/* Logo and Toggle */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          {!isCollapsed && (
            <span className="text-xl font-bold text-blue-600 dark:text-blue-400 truncate">
              ERP Pro
            </span>
          )}
          <button 
            onClick={toggleSidebar}
            className="p-2 text-gray-500 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Toggle Sidebar"
          >
            {isCollapsed ? '▶' : '◀'}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-2 py-4 space-y-2 overflow-y-auto">
          {menuItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) => 
                `flex items-center px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              <span className="text-xl">{item.icon}</span>
              {!isCollapsed && (
                <span className="ml-4 font-medium truncate">{item.name}</span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User / Logout Section */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button 
            onClick={handleLogout}
            className={`flex items-center w-full px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50 transition-colors ${isCollapsed ? 'justify-center' : ''}`}
          >
            <span className="text-lg">🚪</span>
            {!isCollapsed && <span className="ml-3">Logout</span>}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
