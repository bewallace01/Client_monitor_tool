/**
 * Settings Page
 * User Management, Business Management, and Application Configuration
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import UserManagement from '../components/Settings/UserManagement';
import BusinessManagement from '../components/Settings/BusinessManagement';
import GeneralSettings from '../components/Settings/GeneralSettings';
import MonitoringSettings from '../components/Settings/MonitoringSettings';
import APISettings from '../components/Settings/APISettings';
import NotificationSettings from '../components/Settings/NotificationSettings';
import { loadSettings, saveSettings, type AppSettings } from '../services/settings';
import toast from 'react-hot-toast';

type ManagementTabId = 'users' | 'businesses';
type ConfigTabId = 'general' | 'monitoring' | 'api' | 'notifications';

export default function Settings() {
  const { user } = useAuth();
  const [activeManagementTab, setActiveManagementTab] = useState<ManagementTabId>('users');
  const [activeConfigTab, setActiveConfigTab] = useState<ConfigTabId>('general');
  const [appSettings, setAppSettings] = useState<AppSettings>(() => loadSettings());

  // Determine which tabs to show based on user role
  const isSystemAdmin = user?.role === 'system_admin';
  const isBusinessAdmin = user?.role === 'business_admin';
  const canManageUsers = isSystemAdmin || isBusinessAdmin;
  const canManageBusinesses = isSystemAdmin;

  const managementTabs = [
    { id: 'users' as ManagementTabId, label: 'Users', icon: '👥', visible: canManageUsers },
    { id: 'businesses' as ManagementTabId, label: 'Businesses', icon: '🏢', visible: canManageBusinesses },
  ].filter(tab => tab.visible);

  const configTabs = [
    { id: 'general' as ConfigTabId, label: 'General', icon: '⚙️', visible: true },
    { id: 'monitoring' as ConfigTabId, label: 'Monitoring', icon: '📊', visible: true },
    { id: 'api' as ConfigTabId, label: 'API Keys', icon: '🔑', visible: true },
    { id: 'notifications' as ConfigTabId, label: 'Notifications', icon: '🔔', visible: true },
  ];

  // Handler to update settings
  const handleSettingsChange = (newSettings: Partial<AppSettings>) => {
    const updated = {
      ...appSettings,
      ...newSettings,
      general: { ...appSettings.general, ...(newSettings.general || {}) },
      monitoring: { ...appSettings.monitoring, ...(newSettings.monitoring || {}) },
      api: { ...appSettings.api, ...(newSettings.api || {}) },
      notifications: { ...appSettings.notifications, ...(newSettings.notifications || {}) },
    };
    setAppSettings(updated);
    saveSettings(updated);
    toast.success('Settings saved successfully');
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage users, businesses, and application configuration
        </p>
      </div>

      {/* Management Section (Users & Businesses) */}
      {managementTabs.length > 0 && (
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">User & Business Management</h2>

            <div className="flex gap-6">
              {/* Management Tabs */}
              {managementTabs.length > 1 && (
                <div className="w-64 flex-shrink-0">
                  <nav className="space-y-1">
                    {managementTabs.map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveManagementTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                          activeManagementTab === tab.id
                            ? 'bg-blue-50 text-blue-700 font-medium'
                            : 'text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <span className="text-xl">{tab.icon}</span>
                        <span>{tab.label}</span>
                      </button>
                    ))}
                  </nav>
                </div>
              )}

              {/* Management Tab Content */}
              <div className="flex-1">
                {activeManagementTab === 'users' && <UserManagement />}
                {activeManagementTab === 'businesses' && canManageBusinesses && <BusinessManagement />}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Configuration Section (General, Monitoring, API, Notifications) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Configuration</h2>

        <div className="flex gap-6">
          {/* Config Tabs */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {configTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveConfigTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeConfigTab === tab.id
                      ? 'bg-green-50 text-green-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xl">{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Config Tab Content */}
          <div className="flex-1">
            {activeConfigTab === 'general' && (
              <GeneralSettings
                settings={appSettings.general}
                onChange={(general) => handleSettingsChange({ general })}
              />
            )}
            {activeConfigTab === 'monitoring' && (
              <MonitoringSettings
                settings={appSettings.monitoring}
                onChange={(monitoring) => handleSettingsChange({ monitoring })}
              />
            )}
            {activeConfigTab === 'api' && <APISettings />}
            {activeConfigTab === 'notifications' && (
              <NotificationSettings
                settings={appSettings.notifications}
                onChange={(notifications) => handleSettingsChange({ notifications })}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
