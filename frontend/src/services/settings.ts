/**
 * Settings Service
 * Manages application settings using localStorage
 */

export interface GeneralSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'en' | 'es' | 'fr' | 'de';
  timezone: string;
  dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
  itemsPerPage: number;
}

export interface MonitoringSettings {
  checkInterval: number; // minutes
  enableNotifications: boolean;
  notificationSound: boolean;
  autoRefresh: boolean;
  refreshInterval: number; // seconds
  relevanceThreshold: number; // 0-1
}

export interface APISettings {
  newsApiKey: string;
  openaiApiKey: string;
  serperApiKey: string;
  maxRetries: number;
  requestTimeout: number; // seconds
}

export interface NotificationSettings {
  emailNotifications: boolean;
  emailAddress: string;
  notifyOnNewEvents: boolean;
  notifyOnHighRelevance: boolean;
  highRelevanceThreshold: number; // 0-1
  notifyOnErrors: boolean;
}

export interface AppSettings {
  general: GeneralSettings;
  monitoring: MonitoringSettings;
  api: APISettings;
  notifications: NotificationSettings;
}

const SETTINGS_KEY = 'client-monitor-settings';

/**
 * Default settings
 */
const defaultSettings: AppSettings = {
  general: {
    theme: 'system',
    language: 'en',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    dateFormat: 'MM/DD/YYYY',
    itemsPerPage: 20,
  },
  monitoring: {
    checkInterval: 60,
    enableNotifications: true,
    notificationSound: false,
    autoRefresh: true,
    refreshInterval: 30,
    relevanceThreshold: 0.5,
  },
  api: {
    newsApiKey: '',
    openaiApiKey: '',
    serperApiKey: '',
    maxRetries: 3,
    requestTimeout: 30,
  },
  notifications: {
    emailNotifications: false,
    emailAddress: '',
    notifyOnNewEvents: true,
    notifyOnHighRelevance: true,
    highRelevanceThreshold: 0.7,
    notifyOnErrors: true,
  },
};

/**
 * Load settings from localStorage
 */
export function loadSettings(): AppSettings {
  try {
    const stored = localStorage.getItem(SETTINGS_KEY);
    if (!stored) {
      return defaultSettings;
    }
    const parsed = JSON.parse(stored);
    // Merge with defaults to handle new settings
    return {
      general: { ...defaultSettings.general, ...parsed.general },
      monitoring: { ...defaultSettings.monitoring, ...parsed.monitoring },
      api: { ...defaultSettings.api, ...parsed.api },
      notifications: { ...defaultSettings.notifications, ...parsed.notifications },
    };
  } catch (error) {
    console.error('Failed to load settings:', error);
    return defaultSettings;
  }
}

/**
 * Save settings to localStorage
 */
export function saveSettings(settings: AppSettings): void {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch (error) {
    console.error('Failed to save settings:', error);
    throw new Error('Failed to save settings');
  }
}

/**
 * Reset settings to defaults
 */
export function resetSettings(): AppSettings {
  try {
    localStorage.removeItem(SETTINGS_KEY);
    return defaultSettings;
  } catch (error) {
    console.error('Failed to reset settings:', error);
    return defaultSettings;
  }
}

/**
 * Update partial settings
 */
export function updateSettings(partial: Partial<AppSettings>): AppSettings {
  const current = loadSettings();
  const updated = {
    ...current,
    ...partial,
    general: { ...current.general, ...(partial.general || {}) },
    monitoring: { ...current.monitoring, ...(partial.monitoring || {}) },
    api: { ...current.api, ...(partial.api || {}) },
    notifications: { ...current.notifications, ...(partial.notifications || {}) },
  };
  saveSettings(updated);
  return updated;
}

/**
 * Export settings as JSON file
 */
export function exportSettings(): void {
  const settings = loadSettings();
  const blob = new Blob([JSON.stringify(settings, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `client-monitor-settings-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Import settings from JSON file
 */
export function importSettings(file: File): Promise<AppSettings> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target?.result as string);
        saveSettings(imported);
        resolve(imported);
      } catch (error) {
        reject(new Error('Invalid settings file'));
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

/**
 * Get default settings (for reset functionality)
 */
export function getDefaultSettings(): AppSettings {
  return defaultSettings;
}
