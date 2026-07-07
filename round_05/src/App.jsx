import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated } from './features/auth/authSlice';
import Sidebar from './components/Sidebar';
import Dashboard from './features/dashboard/Dashboard';
import EmployeeTable from './features/employee/EmployeeTable';
import AttendancePage from './features/attendance/AttendancePage';
import LeavePage from './features/leave/LeavePage';
import SettingsPage from './features/settings/SettingsPage';
import LoginPage from './features/auth/LoginPage';
import RegisterPage from './features/auth/RegisterPage';
import AdminPanel from './features/settings/AdminPanel';

// PrivateRoute component to protect routes
const PrivateRoute = ({ children }) => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// A simple dashboard layout wrapper
const DashboardLayout = ({ children }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);
  const toggleMobileSidebar = () => setIsMobileOpen((prev) => !prev);
  const closeMobileSidebar = () => setIsMobileOpen(false);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar
        isCollapsed={isCollapsed}
        isMobileOpen={isMobileOpen}
        toggleSidebar={toggleSidebar}
        closeMobileSidebar={closeMobileSidebar}
      />

      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-30 bg-black/30"
          onClick={closeMobileSidebar}
        />
      )}

      <div className={`flex flex-col transition-all duration-300 min-h-screen ml-0 ${isCollapsed ? 'md:ml-20' : 'md:ml-64'}`}>
        <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <button
            onClick={toggleMobileSidebar}
            className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            ☰
          </button>
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">ERP Pro</span>
        </div>

        <main className="p-4 md:p-8 flex-1">
          {children}
        </main>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route path="/" element={
        <PrivateRoute>
          <DashboardLayout>
            <Dashboard />
          </DashboardLayout>
        </PrivateRoute>
      } />
      
      <Route path="/employees" element={
        <PrivateRoute>
          <DashboardLayout>
            <EmployeeTable />
          </DashboardLayout>
        </PrivateRoute>
      } />
      
      <Route path="/attendance" element={
        <PrivateRoute>
          <DashboardLayout>
            <AttendancePage />
          </DashboardLayout>
        </PrivateRoute>
      } />
      
      <Route path="/leaves" element={
        <PrivateRoute>
          <DashboardLayout>
            <LeavePage />
          </DashboardLayout>
        </PrivateRoute>
      } />
      
      <Route path="/settings" element={
        <PrivateRoute>
          <DashboardLayout>
            <SettingsPage />
          </DashboardLayout>
        </PrivateRoute>
      } />

      <Route path="/admin" element={
        <PrivateRoute>
          <DashboardLayout>
            <AdminPanel />
          </DashboardLayout>
        </PrivateRoute>
      } />
      
      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
