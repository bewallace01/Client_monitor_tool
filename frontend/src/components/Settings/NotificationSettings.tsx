/**
 * NotificationSettings Component
 * Notification preferences settings tab
 */

import type { NotificationSettings as NotificationSettingsType } from '../../services/settings';

interface NotificationSettingsProps {
  settings: NotificationSettingsType;
  onChange: (settings: Partial<NotificationSettingsType>) => void;
}

export default function NotificationSettings({
  settings,
  onChange,
}: NotificationSettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Notification Settings
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Configure how and when you receive notifications about events.
        </p>
      </div>

      {/* Email Notifications */}
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            type="checkbox"
            checked={settings.emailNotifications}
            onChange={(e) => onChange({ emailNotifications: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
        </div>
        <div className="ml-3">
          <label className="text-sm font-medium text-gray-700">
            Enable Email Notifications
          </label>
          <p className="text-xs text-gray-500">
            Receive email alerts for important events
          </p>
        </div>
      </div>

      {/* Email Address */}
      {settings.emailNotifications && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Address
          </label>
          <input
            type="email"
            value={settings.emailAddress}
            onChange={(e) => onChange({ emailAddress: e.target.value })}
            placeholder="your.email@example.com"
            className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">
            Where to send notification emails
          </p>
        </div>
      )}

      <div className="border-t border-gray-200 pt-6">
        <h4 className="text-sm font-semibold text-gray-900 mb-4">
          Notification Triggers
        </h4>

        {/* Notify on New Events */}
        <div className="flex items-start mb-4">
          <div className="flex items-center h-5">
            <input
              type="checkbox"
              checked={settings.notifyOnNewEvents}
              onChange={(e) => onChange({ notifyOnNewEvents: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
          <div className="ml-3">
            <label className="text-sm font-medium text-gray-700">
              Notify on New Events
            </label>
            <p className="text-xs text-gray-500">
              Get notified when new events are discovered
            </p>
          </div>
        </div>

        {/* Notify on High Relevance */}
        <div className="flex items-start mb-4">
          <div className="flex items-center h-5">
            <input
              type="checkbox"
              checked={settings.notifyOnHighRelevance}
              onChange={(e) =>
                onChange({ notifyOnHighRelevance: e.target.checked })
              }
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
          <div className="ml-3">
            <label className="text-sm font-medium text-gray-700">
              Notify on High Relevance Events
            </label>
            <p className="text-xs text-gray-500">
              Get notified for events above the relevance threshold
            </p>
          </div>
        </div>

        {/* High Relevance Threshold */}
        {settings.notifyOnHighRelevance && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              High Relevance Threshold:{' '}
              {Math.round(settings.highRelevanceThreshold * 100)}%
            </label>
            <input
              type="range"
              min="50"
              max="100"
              step="5"
              value={settings.highRelevanceThreshold * 100}
              onChange={(e) =>
                onChange({ highRelevanceThreshold: parseInt(e.target.value) / 100 })
              }
              className="w-full max-w-md"
            />
            <p className="text-xs text-gray-500 mt-1">
              Minimum relevance score to trigger notifications (50-100%)
            </p>
          </div>
        )}

        {/* Notify on Errors */}
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              type="checkbox"
              checked={settings.notifyOnErrors}
              onChange={(e) => onChange({ notifyOnErrors: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
          <div className="ml-3">
            <label className="text-sm font-medium text-gray-700">
              Notify on Errors
            </label>
            <p className="text-xs text-gray-500">
              Get notified when monitoring jobs fail
            </p>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mt-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-blue-400 text-xl">ℹ️</span>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              Email notifications require server configuration. If you're running the
              app locally, browser notifications will be used instead.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
