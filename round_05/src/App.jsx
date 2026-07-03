import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './features/dashboard/Dashboard';
import EmployeeTable from './features/employee/EmployeeTable';
import AttendancePage from './features/attendance/AttendancePage';
import LeavePage from './features/leave/LeavePage';
import SettingsPage from './features/settings/SettingsPage';

// A simple dashboard layout wrapper
const DashboardLayout = ({ children }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const toggleSidebar = () => setIsCollapsed(!isCollapsed);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar isCollapsed={isCollapsed} toggleSidebar={toggleSidebar} />
      <div className={`flex-1 transition-all duration-300 ${isCollapsed ? 'ml-20' : 'ml-64'}`}>
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Routes>
      <Route path="/" element={
        <DashboardLayout>
          <Dashboard />
        </DashboardLayout>
      } />
      
      <Route path="/employees" element={
        <DashboardLayout>
          <EmployeeTable />
        </DashboardLayout>
      } />
      
      <Route path="/attendance" element={
        <DashboardLayout>
          <AttendancePage />
        </DashboardLayout>
      } />
      
      <Route path="/leaves" element={
        <DashboardLayout>
          <LeavePage />
        </DashboardLayout>
      } />
      
      <Route path="/settings" element={
        <DashboardLayout>
          <SettingsPage />
        </DashboardLayout>
      } />
      
      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
