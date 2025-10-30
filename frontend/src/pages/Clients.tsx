/**
 * Clients Page
 * Main page for managing clients with CRUD operations
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getClients, deleteClient, getIndustries, getTiers } from '../services/clients';
import type { Client, ClientsFilters } from '../services/clients';
import ClientList from '../components/Clients/ClientList';
import ClientForm from '../components/Clients/ClientForm';
import ClientDetail from '../components/Clients/ClientDetail';

export default function Clients() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<ClientsFilters>({
    skip: 0,
    limit: 20,
    sort_by: 'updated_at',
    sort_desc: true,
  });
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState<Client | null>(null);

  // Fetch clients with filters
  const { data, isLoading, error } = useQuery({
    queryKey: ['clients', filters],
    queryFn: () => getClients(filters),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch filter options
  const { data: industries } = useQuery({
    queryKey: ['industries'],
    queryFn: getIndustries,
  });

  const { data: tiers } = useQuery({
    queryKey: ['tiers'],
    queryFn: getTiers,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (clientId: string) => deleteClient(clientId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setClientToDelete(null);
    },
  });

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setIsFormOpen(true);
  };

  const handleView = (client: Client) => {
    setSelectedClient(client);
    setIsDetailOpen(true);
  };

  const handleDelete = (client: Client) => {
    setClientToDelete(client);
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({
      ...prev,
      skip: (page - 1) * (prev.limit || 20),
    }));
  };

  const handleSearch = (search: string) => {
    setFilters((prev) => ({
      ...prev,
      search: search || undefined,
      skip: 0, // Reset to first page
    }));
  };

  const handleFilterChange = (filterKey: string, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [filterKey]: value === '' ? undefined : value,
      skip: 0, // Reset to first page
    }));
  };

  if (error) {
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
          <p className="text-gray-600 mt-2">Manage your client accounts</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">
            Failed to load clients. Please check if the API server is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
          <p className="text-gray-600 mt-2">
            Manage your client accounts and monitoring settings
          </p>
        </div>
        <button
          onClick={() => {
            setSelectedClient(null);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <span className="text-lg">+</span>
          Add Client
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              placeholder="Search clients..."
              value={filters.search || ''}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Industry Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry
            </label>
            <select
              value={filters.industry || ''}
              onChange={(e) => handleFilterChange('industry', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Industries</option>
              {industries?.map((industry) => (
                <option key={industry} value={industry}>
                  {industry}
                </option>
              ))}
            </select>
          </div>

          {/* Tier Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tier
            </label>
            <select
              value={filters.tier || ''}
              onChange={(e) => handleFilterChange('tier', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Tiers</option>
              {tiers?.map((tier) => (
                <option key={tier} value={tier}>
                  {tier}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.is_active === undefined ? '' : filters.is_active ? 'active' : 'inactive'}
              onChange={(e) =>
                handleFilterChange(
                  'is_active',
                  e.target.value === '' ? undefined : e.target.value === 'active'
                )
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Client List */}
      <ClientList
        clients={data?.items || []}
        loading={isLoading}
        currentPage={Math.floor((filters.skip || 0) / (filters.limit || 20)) + 1}
        totalPages={data?.total_pages || 1}
        onPageChange={handlePageChange}
        onEdit={handleEdit}
        onView={handleView}
        onDelete={handleDelete}
      />

      {/* Client Form Modal */}
      {isFormOpen && (
        <ClientForm
          client={selectedClient}
          onClose={() => {
            setIsFormOpen(false);
            setSelectedClient(null);
          }}
          onSuccess={() => {
            setIsFormOpen(false);
            setSelectedClient(null);
            queryClient.invalidateQueries({ queryKey: ['clients'] });
          }}
        />
      )}

      {/* Client Detail Modal */}
      {isDetailOpen && selectedClient && (
        <ClientDetail
          client={selectedClient}
          onClose={() => {
            setIsDetailOpen(false);
            setSelectedClient(null);
          }}
          onEdit={() => {
            setIsDetailOpen(false);
            setIsFormOpen(true);
          }}
        />
      )}

      {/* Delete Confirmation Modal */}
      {clientToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Delete Client
            </h3>
            <p className="text-gray-600 mb-4">
              Are you sure you want to delete <strong>{clientToDelete.name}</strong>?
              This will also delete all associated events and cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setClientToDelete(null)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (clientToDelete) {
                    deleteMutation.mutate(clientToDelete.id);
                  }
                }}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
