/**
 * MonitoringSettings Component
 * Monitoring and automation settings tab
 */

import type { MonitoringSettings as MonitoringSettingsType } from '../../services/settings';

interface MonitoringSettingsProps {
  settings: MonitoringSettingsType;
  onChange: (settings: Partial<MonitoringSettingsType>) => void;
}

export default function MonitoringSettings({
  settings,
  onChange,
}: MonitoringSettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Monitoring Settings
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Configure monitoring intervals and automation behavior.
        </p>
      </div>

      {/* Check Interval */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Check Interval (minutes)
        </label>
        <input
          type="number"
          min="5"
          max="1440"
          value={settings.checkInterval}
          onChange={(e) =>
            onChange({ checkInterval: parseInt(e.target.value) || 60 })
          }
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          How often to automatically check for new events (5-1440 minutes)
        </p>
      </div>

      {/* Enable Notifications */}
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            type="checkbox"
            checked={settings.enableNotifications}
            onChange={(e) => onChange({ enableNotifications: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
        </div>
        <div className="ml-3">
          <label className="text-sm font-medium text-gray-700">
            Enable Notifications
          </label>
          <p className="text-xs text-gray-500">
            Show browser notifications for new events and updates
          </p>
        </div>
      </div>

      {/* Notification Sound */}
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            type="checkbox"
            checked={settings.notificationSound}
            onChange={(e) => onChange({ notificationSound: e.target.checked })}
            disabled={!settings.enableNotifications}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
          />
        </div>
        <div className="ml-3">
          <label className="text-sm font-medium text-gray-700">
            Notification Sound
          </label>
          <p className="text-xs text-gray-500">
            Play a sound when notifications appear
          </p>
        </div>
      </div>

      {/* Auto Refresh */}
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            type="checkbox"
            checked={settings.autoRefresh}
            onChange={(e) => onChange({ autoRefresh: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
        </div>
        <div className="ml-3">
          <label className="text-sm font-medium text-gray-700">
            Auto-Refresh Data
          </label>
          <p className="text-xs text-gray-500">
            Automatically refresh data in the background
          </p>
        </div>
      </div>

      {/* Refresh Interval */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Refresh Interval (seconds)
        </label>
        <input
          type="number"
          min="10"
          max="300"
          value={settings.refreshInterval}
          onChange={(e) =>
            onChange({ refreshInterval: parseInt(e.target.value) || 30 })
          }
          disabled={!settings.autoRefresh}
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
        />
        <p className="text-xs text-gray-500 mt-1">
          How often to refresh data when auto-refresh is enabled (10-300 seconds)
        </p>
      </div>

      {/* Relevance Threshold */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Relevance Threshold: {Math.round(settings.relevanceThreshold * 100)}%
        </label>
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={settings.relevanceThreshold * 100}
          onChange={(e) =>
            onChange({ relevanceThreshold: parseInt(e.target.value) / 100 })
          }
          className="w-full max-w-md"
        />
        <p className="text-xs text-gray-500 mt-1">
          Minimum relevance score for events to trigger notifications
        </p>
      </div>
    </div>
  );
}
