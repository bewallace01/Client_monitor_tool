/**
 * APISettings Component
 * API configuration settings tab - Supports multi-API configuration with testing
 */

import { useState, useEffect } from 'react';
import {
  getAvailableProviders,
  getAPIConfigs,
  createAPIConfig,
  deleteAPIConfig,
  testAPIConnection,
  getUsageStats,
  type APIProvider,
  type APIConfig,
  type APIUsageStats,
} from '../../services/apiConfigs';
import { useAuth } from '../../contexts/AuthContext';

export default function APISettings() {
  const { user } = useAuth();
  const [availableProviders, setAvailableProviders] = useState<APIProvider[]>([]);
  const [configurations, setConfigurations] = useState<APIConfig[]>([]);
  const [usageStats, setUsageStats] = useState<APIUsageStats[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    apiKey: '',
    apiSecret: '',
    maxTokensPerMonth: '',
    rateLimitPerHour: '',
    costPer1kTokens: '',
  });

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    if (!user?.business_id) return;

    try {
      setLoading(true);
      const [providers, configs, stats] = await Promise.all([
        getAvailableProviders(),
        getAPIConfigs(user.business_id),
        getUsageStats(user.business_id),
      ]);

      setAvailableProviders(providers);
      setConfigurations(configs);
      setUsageStats(stats);
    } catch (error) {
      console.error('Failed to load API settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAPI = () => {
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setSelectedProvider('');
    setFormData({
      apiKey: '',
      apiSecret: '',
      maxTokensPerMonth: '',
      rateLimitPerHour: '',
      costPer1kTokens: '',
    });
  };

  const handleSubmitForm = async () => {
    if (!user?.business_id || !selectedProvider) return;

    const provider = availableProviders.find(p => p.provider === selectedProvider);
    if (!provider) return;

    try {
      await createAPIConfig({
        business_id: user.business_id,
        provider: selectedProvider,
        provider_name: provider.display_name,
        api_key: formData.apiKey || undefined,
        api_secret: formData.apiSecret || undefined,
        max_tokens_per_month: formData.maxTokensPerMonth ? parseInt(formData.maxTokensPerMonth) : undefined,
        rate_limit_per_hour: formData.rateLimitPerHour ? parseInt(formData.rateLimitPerHour) : undefined,
        cost_per_1k_tokens: formData.costPer1kTokens ? parseFloat(formData.costPer1kTokens) : undefined,
        is_active: true,
      });

      await loadData();
      handleCancelForm();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create API configuration');
    }
  };

  const handleTestConnection = async (configId: string) => {
    if (!user?.business_id) return;

    setTesting(configId);
    try {
      const result = await testAPIConnection(configId, user.business_id);
      alert(
        `Connection Test ${result.success ? 'Successful' : 'Failed'}\n\n${result.message}${
          result.response_time_ms ? `\n\nResponse time: ${result.response_time_ms}ms` : ''
        }`
      );
      await loadData();
    } catch (error) {
      alert('Failed to test API connection');
    } finally {
      setTesting(null);
    }
  };

  const handleDeleteConfig = async (configId: string) => {
    if (!user?.business_id) return;
    if (!confirm('Are you sure you want to delete this API configuration?')) return;

    try {
      await deleteAPIConfig(configId, user.business_id);
      await loadData();
    } catch (error) {
      alert('Failed to delete API configuration');
    }
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      newsapi: '📰',
      openai: '🤖',
      google_search: '🔍',
      hubspot: '🎯',
      salesforce: '☁️',
      serper: '🔎',
      anthropic: '🧠',
    };
    return icons[provider] || '🔌';
  };

  const getStatusBadge = (config: APIConfig) => {
    if (!config.last_test_status) {
      return <span className="text-gray-500 text-xs">Not tested</span>;
    }

    if (config.last_test_status === 'success') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          ✓ Connected
        </span>
      );
    }

    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
        ✗ Failed
      </span>
    );
  };

  const getUsagePercentage = (configId: string) => {
    const stats = usageStats.find(s => s.config_id === configId);
    return stats?.usage_percentage || 0;
  };

  const availableProvidersToAdd = availableProviders.filter(
    provider => !configurations.some(config => config.provider === provider.provider)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading API configurations...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">API Configurations</h3>
          <p className="text-sm text-gray-600">
            Manage API keys and credentials for external services. Each API can be configured with usage limits and tested independently.
          </p>
        </div>
        {availableProvidersToAdd.length > 0 && !showForm && (
          <button
            onClick={handleAddAPI}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Add API
          </button>
        )}
      </div>

      {/* Add API Form */}
      {showForm && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h4 className="text-md font-semibold text-gray-900 mb-4">Add New API Configuration</h4>

          {/* Provider Dropdown */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select API Provider
            </label>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">-- Select a provider --</option>
              {availableProvidersToAdd.map((provider) => (
                <option key={provider.provider} value={provider.provider}>
                  {getProviderIcon(provider.provider)} {provider.display_name}
                </option>
              ))}
            </select>
            {selectedProvider && (
              <p className="text-xs text-gray-600 mt-2">
                {availableProviders.find(p => p.provider === selectedProvider)?.description}
              </p>
            )}
          </div>

          {selectedProvider && (
            <>
              {/* API Key */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key *
                </label>
                <input
                  type="password"
                  value={formData.apiKey}
                  onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                  placeholder="Enter your API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {availableProviders.find(p => p.provider === selectedProvider)?.documentation_url && (
                  <a
                    href={availableProviders.find(p => p.provider === selectedProvider)!.documentation_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline mt-1 inline-block"
                  >
                    Get API key from documentation →
                  </a>
                )}
              </div>

              {/* API Secret (for providers that need it) */}
              {availableProviders.find(p => p.provider === selectedProvider)?.requires_secret && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Secret / Additional Credential
                  </label>
                  <input
                    type="password"
                    value={formData.apiSecret}
                    onChange={(e) => setFormData({ ...formData, apiSecret: e.target.value })}
                    placeholder="Enter API secret or search engine ID"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}

              {/* Max Tokens Per Month */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum Tokens/Requests Per Month
                </label>
                <input
                  type="number"
                  value={formData.maxTokensPerMonth}
                  onChange={(e) => setFormData({ ...formData, maxTokensPerMonth: e.target.value })}
                  placeholder="e.g., 100000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Set a limit to prevent overuse and unexpected costs
                </p>
              </div>

              {/* Rate Limit Per Hour */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rate Limit (Requests Per Hour)
                </label>
                <input
                  type="number"
                  value={formData.rateLimitPerHour}
                  onChange={(e) => setFormData({ ...formData, rateLimitPerHour: e.target.value })}
                  placeholder="e.g., 100"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Cost Per 1K Tokens */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cost Per 1,000 Tokens (USD)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={formData.costPer1kTokens}
                  onChange={(e) => setFormData({ ...formData, costPer1kTokens: e.target.value })}
                  placeholder="e.g., 0.002"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Used to calculate estimated monthly costs
                </p>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSubmitForm}
                  disabled={!formData.apiKey}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Save API Configuration
                </button>
                <button
                  onClick={handleCancelForm}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Configured APIs List */}
      <div className="space-y-4">
        {configurations.length === 0 ? (
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <p className="text-gray-600 mb-4">No API configurations yet</p>
            <p className="text-sm text-gray-500">
              Click "Add API" to configure your first API integration
            </p>
          </div>
        ) : (
          configurations.map((config) => (
            <div
              key={config.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{getProviderIcon(config.provider)}</span>
                  <div>
                    <h4 className="text-md font-semibold text-gray-900">
                      {config.provider_name}
                    </h4>
                    <p className="text-sm text-gray-500">{config.provider}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(config)}
                  {config.is_active ? (
                    <span className="text-green-600 text-xs font-medium">Active</span>
                  ) : (
                    <span className="text-gray-400 text-xs font-medium">Inactive</span>
                  )}
                </div>
              </div>

              {/* API Key Display */}
              <div className="mb-4">
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  API Key
                </label>
                <div className="flex gap-2">
                  <code className="flex-1 px-3 py-2 bg-gray-50 rounded border border-gray-200 text-sm font-mono">
                    {config.api_key_masked || '••••••••'}
                  </code>
                </div>
              </div>

              {/* Usage Statistics */}
              {config.max_tokens_per_month && (
                <div className="mb-4">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Usage this month</span>
                    <span>
                      {config.tokens_used_current_month.toLocaleString()} / {config.max_tokens_per_month.toLocaleString()} tokens
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        getUsagePercentage(config.id) > 90
                          ? 'bg-red-500'
                          : getUsagePercentage(config.id) > 75
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(getUsagePercentage(config.id), 100)}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Cost Estimate */}
              {config.estimated_monthly_cost !== undefined && config.estimated_monthly_cost > 0 && (
                <div className="mb-4 text-sm text-gray-600">
                  Estimated monthly cost: <span className="font-semibold">${config.estimated_monthly_cost.toFixed(2)}</span>
                </div>
              )}

              {/* Last Test Status */}
              {config.last_test_message && (
                <div className="mb-4 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                  {config.last_test_message}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleTestConnection(config.id)}
                  disabled={testing === config.id}
                  className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {testing === config.id ? 'Testing...' : '🔌 Test Connection'}
                </button>
                <button
                  onClick={() => handleDeleteConfig(config.id)}
                  className="px-3 py-1.5 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Security Notice */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-yellow-400 text-xl">⚠️</span>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              <strong>Security Notice:</strong> API keys are encrypted and stored securely in the database.
              They are never exposed in full after initial configuration. Only administrators can manage API configurations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
