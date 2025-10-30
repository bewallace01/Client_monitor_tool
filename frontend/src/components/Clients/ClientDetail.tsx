/**
 * ClientDetail Component
 * Modal displaying full client details
 */

import type { Client } from '../../services/clients';

interface ClientDetailProps {
  client: Client;
  onClose: () => void;
  onEdit: () => void;
}

export default function ClientDetail({ client, onClose, onEdit }: ClientDetailProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">{client.name}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Status Badge */}
          <div>
            <span
              className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${
                client.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {client.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Domain</label>
              <p className="text-gray-900">
                {client.domain ? (
                  <a
                    href={`https://${client.domain}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {client.domain}
                  </a>
                ) : (
                  '-'
                )}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Industry</label>
              <p className="text-gray-900">{client.industry || '-'}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Tier</label>
              <p className="text-gray-900">{client.tier || '-'}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Account Owner</label>
              <p className="text-gray-900">{client.account_owner || '-'}</p>
            </div>
          </div>

          {/* Description */}
          {client.description && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Description</label>
              <p className="text-gray-900">{client.description}</p>
            </div>
          )}

          {/* Search Keywords */}
          {client.search_keywords && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Search Keywords
              </label>
              <div className="flex flex-wrap gap-2">
                {client.search_keywords.split(',').map((keyword, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-50 text-blue-700 text-sm rounded"
                  >
                    {keyword.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          {client.notes && (
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Notes</label>
              <p className="text-gray-900 whitespace-pre-wrap">{client.notes}</p>
            </div>
          )}

          {/* Timestamps */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Created</label>
              <p className="text-sm text-gray-900">
                {new Date(client.created_at).toLocaleString()}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Last Updated</label>
              <p className="text-sm text-gray-900">
                {new Date(client.updated_at).toLocaleString()}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">Last Checked</label>
              <p className="text-sm text-gray-900">
                {client.last_checked_at
                  ? new Date(client.last_checked_at).toLocaleString()
                  : 'Never'}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            <button
              onClick={onEdit}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Edit Client
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
