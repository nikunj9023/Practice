import React, { useState } from 'react';
import api from '../../services/api';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  
  const handleInvite = (e) => {
    e.preventDefault();
    if (inviteEmail) {
      alert(`Invitation sent to ${inviteEmail}`);
      setInviteEmail('');
      setIsInviteModalOpen(false);
    }
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 max-w-6xl">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">Admin Panel</h2>
      
      <div className="flex space-x-4 border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          onClick={() => setActiveTab('users')}
          className={`py-2 px-4 font-medium text-sm transition-colors ${activeTab === 'users' ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
        >
          User Management
        </button>
        <button 
          onClick={() => setActiveTab('system')}
          className={`py-2 px-4 font-medium text-sm transition-colors ${activeTab === 'system' ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
        >
          System Configuration
        </button>
        <button 
          onClick={() => setActiveTab('logs')}
          className={`py-2 px-4 font-medium text-sm transition-colors ${activeTab === 'logs' ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
        >
          Audit Logs
        </button>
      </div>

      <div className="space-y-6">
        {activeTab === 'users' && (
          <section>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300">System Users</h3>
              <button 
                onClick={() => setIsInviteModalOpen(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 text-sm rounded-md transition-colors"
              >
                + Invite User
              </button>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-8 border border-gray-100 dark:border-gray-700 text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-2">Configure user access roles and permissions.</p>
              <p className="text-xs text-gray-400">Admin privileges are required to modify these settings.</p>
            </div>
          </section>
        )}

        {activeTab === 'system' && (
          <section>
             <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">Global ERP Settings</h3>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Company Information</h4>
                  <input type="text" placeholder="Company Name" className="w-full mt-1 mb-3 px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600" defaultValue="ERP Pro Inc." />
                  <input type="email" placeholder="Contact Email" className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600" defaultValue="admin@erppro.com" />
                </div>
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Data Management</h4>
                  <button className="w-full mb-3 text-left px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600">Download Database Backup</button>
                  <button className="w-full text-left px-4 py-2 text-red-600 bg-red-50 dark:bg-red-900/20 rounded-md hover:bg-red-100 dark:hover:bg-red-900/40">Purge Old Records (30+ days)</button>
                </div>
             </div>
          </section>
        )}

        {activeTab === 'logs' && (
          <section>
            <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-700">
                <div>
                  <span className="font-medium text-gray-800 dark:text-gray-200 text-sm">System Update</span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Database migrated successfully.</p>
                </div>
                <span className="text-xs text-gray-400">2 mins ago</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-700">
                <div>
                  <span className="font-medium text-gray-800 dark:text-gray-200 text-sm">Admin Access</span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Super admin logged in from 192.168.1.1.</p>
                </div>
                <span className="text-xs text-gray-400">1 hour ago</span>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Invite User Modal */}
      {isInviteModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
          <div className="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-opacity-80" aria-hidden="true" onClick={() => setIsInviteModalOpen(false)}></div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block overflow-hidden text-left align-bottom transition-all transform bg-white dark:bg-gray-800 rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <form onSubmit={handleInvite}>
                <div className="px-4 pt-5 pb-4 bg-white dark:bg-gray-800 sm:p-6 sm:pb-4">
                  <h3 className="text-lg font-medium leading-6 text-gray-900 dark:text-white" id="modal-title">
                    Invite New User
                  </h3>
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">User Email</label>
                    <input 
                      type="email" 
                      required 
                      value={inviteEmail} 
                      onChange={e => setInviteEmail(e.target.value)} 
                      placeholder="colleague@company.com"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
                    />
                    <p className="mt-2 text-xs text-gray-500">They will receive an email with instructions to set up their account.</p>
                  </div>
                </div>
                <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 sm:px-6 sm:flex sm:flex-row-reverse">
                  <button type="submit" className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm">
                    Send Invitation
                  </button>
                  <button type="button" onClick={() => setIsInviteModalOpen(false)} className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
