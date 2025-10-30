/**
 * GeneralSettings Component
 * General application settings tab
 */

import type { GeneralSettings as GeneralSettingsType } from '../../services/settings';

interface GeneralSettingsProps {
  settings: GeneralSettingsType;
  onChange: (settings: Partial<GeneralSettingsType>) => void;
}

export default function GeneralSettings({ settings, onChange }: GeneralSettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">General Settings</h3>
        <p className="text-sm text-gray-600 mb-6">
          Configure general application preferences and display options.
        </p>
      </div>

      {/* Theme */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Theme
        </label>
        <select
          value={settings.theme}
          onChange={(e) =>
            onChange({ theme: e.target.value as 'light' | 'dark' | 'system' })
          }
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="system">System Default</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          Choose your preferred color scheme
        </p>
      </div>

      {/* Language */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={settings.language}
          onChange={(e) =>
            onChange({ language: e.target.value as 'en' | 'es' | 'fr' | 'de' })
          }
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          Select your preferred language
        </p>
      </div>

      {/* Timezone */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timezone
        </label>
        <input
          type="text"
          value={settings.timezone}
          onChange={(e) => onChange({ timezone: e.target.value })}
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="UTC"
        />
        <p className="text-xs text-gray-500 mt-1">
          Your current timezone (e.g., America/New_York)
        </p>
      </div>

      {/* Date Format */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Date Format
        </label>
        <select
          value={settings.dateFormat}
          onChange={(e) =>
            onChange({
              dateFormat: e.target.value as 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD',
            })
          }
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="MM/DD/YYYY">MM/DD/YYYY (US)</option>
          <option value="DD/MM/YYYY">DD/MM/YYYY (European)</option>
          <option value="YYYY-MM-DD">YYYY-MM-DD (ISO)</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          How dates should be displayed throughout the app
        </p>
      </div>

      {/* Items Per Page */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Items Per Page
        </label>
        <select
          value={settings.itemsPerPage}
          onChange={(e) => onChange({ itemsPerPage: parseInt(e.target.value) })}
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          Default number of items to display in lists
        </p>
      </div>
    </div>
  );
}
