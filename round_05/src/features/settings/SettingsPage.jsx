import React from 'react';

const SettingsPage = () => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 max-w-4xl">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">Settings</h2>
      
      <div className="space-y-6">
        <section>
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">General Settings</h3>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Settings content will go here. This page is currently under construction.</p>
        </section>
        
        <section>
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">Account Preferences</h3>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Preferences will go here.</p>
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;
