/**
 * Business Management Component
 * Manage businesses - create, edit, delete (System Admin only)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
  getBusinesses,
  createBusiness,
  updateBusiness,
  deleteBusiness,
  activateBusiness,
  deactivateBusiness,
  type Business,
  type BusinessCreate,
  type BusinessUpdate,
} from '../../services/businesses';

export default function BusinessManagement() {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null);
  const [filters, setFilters] = useState({
    is_active: undefined as boolean | undefined,
    subscription_tier: undefined as string | undefined,
  });

  // Query businesses
  const { data: businessesData, isLoading: businessesLoading } = useQuery({
    queryKey: ['businesses', filters],
    queryFn: () => getBusinesses(filters),
  });

  // Create business mutation
  const createMutation = useMutation({
    mutationFn: (businessData: BusinessCreate) => createBusiness(businessData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['businesses'] });
      toast.success('Business created successfully');
      setIsCreateModalOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create business');
    },
  });

  // Update business mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: BusinessUpdate }) =>
      updateBusiness(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['businesses'] });
      toast.success('Business updated successfully');
      setIsEditModalOpen(false);
      setSelectedBusiness(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update business');
    },
  });

  // Delete business mutation
  const deleteMutation = useMutation({
    mutationFn: (businessId: string) => deleteBusiness(businessId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['businesses'] });
      toast.success('Business deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete business');
    },
  });

  // Toggle active status mutation
  const toggleActiveMutation = useMutation({
    mutationFn: ({ businessId, isActive }: { businessId: string; isActive: boolean }) =>
      isActive ? deactivateBusiness(businessId) : activateBusiness(businessId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['businesses'] });
      toast.success('Business status updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update business status');
    },
  });

  const handleDeleteBusiness = (business: Business) => {
    if (
      window.confirm(
        `Are you sure you want to delete business "${business.name}"? This will also affect all users and data associated with this business.`
      )
    ) {
      deleteMutation.mutate(business.id);
    }
  };

  const handleEditBusiness = (business: Business) => {
    setSelectedBusiness(business);
    setIsEditModalOpen(true);
  };

  const getTierBadgeColor = (tier: string | null) => {
    if (!tier) return 'bg-gray-100 text-gray-800';
    switch (tier.toLowerCase()) {
      case 'enterprise':
        return 'bg-purple-100 text-purple-800';
      case 'professional':
        return 'bg-blue-100 text-blue-800';
      case 'starter':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusBadgeColor = (status: string | null) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'trial':
        return 'bg-yellow-100 text-yellow-800';
      case 'suspended':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Business Management</h2>
            <p className="text-sm text-gray-600 mt-1">
              Manage all businesses on the platform
            </p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add Business
          </button>
        </div>

        {/* Filters */}
        <div className="mt-4 flex gap-4">
          <select
            value={filters.is_active === undefined ? '' : filters.is_active.toString()}
            onChange={(e) =>
              setFilters({
                ...filters,
                is_active: e.target.value === '' ? undefined : e.target.value === 'true',
              })
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>

          <select
            value={filters.subscription_tier || ''}
            onChange={(e) =>
              setFilters({
                ...filters,
                subscription_tier: e.target.value || undefined,
              })
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Tiers</option>
            <option value="Enterprise">Enterprise</option>
            <option value="Professional">Professional</option>
            <option value="Starter">Starter</option>
          </select>
        </div>
      </div>

      {/* Business List */}
      <div className="overflow-x-auto">
        {businessesLoading ? (
          <div className="p-8 text-center text-gray-500">Loading businesses...</div>
        ) : !businessesData?.items.length ? (
          <div className="p-8 text-center text-gray-500">No businesses found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Business
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Domain
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Industry
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Subscription
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {businessesData?.items.map((business) => (
                <tr key={business.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="font-medium text-gray-900">{business.name}</div>
                      {business.contact_email && (
                        <div className="text-sm text-gray-500">{business.contact_email}</div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {business.domain || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {business.industry || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-col gap-1">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getTierBadgeColor(
                          business.subscription_tier
                        )}`}
                      >
                        {business.subscription_tier || 'No Tier'}
                      </span>
                      {business.subscription_status && (
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(
                            business.subscription_status
                          )}`}
                        >
                          {business.subscription_status}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() =>
                        toggleActiveMutation.mutate({
                          businessId: business.id,
                          isActive: business.is_active,
                        })
                      }
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        business.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {business.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleEditBusiness(business)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteBusiness(business)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {businessesData && businessesData.total_pages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {businessesData.items.length} of {businessesData.total} businesses
          </div>
          <div className="text-sm text-gray-600">
            Page {businessesData.page} of {businessesData.total_pages}
          </div>
        </div>
      )}

      {/* Create Business Modal */}
      {isCreateModalOpen && (
        <BusinessFormModal
          mode="create"
          onSubmit={(data) => createMutation.mutate(data)}
          onClose={() => setIsCreateModalOpen(false)}
          isSubmitting={createMutation.isPending}
        />
      )}

      {/* Edit Business Modal */}
      {isEditModalOpen && selectedBusiness && (
        <BusinessFormModal
          mode="edit"
          business={selectedBusiness}
          onSubmit={(data) =>
            updateMutation.mutate({ id: selectedBusiness.id, updates: data })
          }
          onClose={() => {
            setIsEditModalOpen(false);
            setSelectedBusiness(null);
          }}
          isSubmitting={updateMutation.isPending}
        />
      )}
    </div>
  );
}

// Business Form Modal Component
interface BusinessFormModalProps {
  mode: 'create' | 'edit';
  business?: Business;
  onSubmit: (data: BusinessCreate | BusinessUpdate) => void;
  onClose: () => void;
  isSubmitting: boolean;
}

function BusinessFormModal({
  mode,
  business,
  onSubmit,
  onClose,
  isSubmitting,
}: BusinessFormModalProps) {
  const [formData, setFormData] = useState({
    name: business?.name || '',
    domain: business?.domain || '',
    industry: business?.industry || '',
    size: business?.size || '',
    contact_email: business?.contact_email || '',
    contact_phone: business?.contact_phone || '',
    address: business?.address || '',
    subscription_tier: business?.subscription_tier || '',
    subscription_status: business?.subscription_status || '',
    is_active: business?.is_active !== undefined ? business.is_active : true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === 'create') {
      onSubmit({
        name: formData.name,
        domain: formData.domain || null,
        industry: formData.industry || null,
        size: formData.size || null,
        contact_email: formData.contact_email || null,
        contact_phone: formData.contact_phone || null,
        address: formData.address || null,
        subscription_tier: formData.subscription_tier || null,
        subscription_status: formData.subscription_status || null,
        is_active: formData.is_active,
      });
    } else {
      // For edit, only include changed fields
      const updates: BusinessUpdate = {};
      if (formData.name !== business?.name) updates.name = formData.name;
      if (formData.domain !== business?.domain) updates.domain = formData.domain || null;
      if (formData.industry !== business?.industry) updates.industry = formData.industry || null;
      if (formData.size !== business?.size) updates.size = formData.size || null;
      if (formData.contact_email !== business?.contact_email)
        updates.contact_email = formData.contact_email || null;
      if (formData.contact_phone !== business?.contact_phone)
        updates.contact_phone = formData.contact_phone || null;
      if (formData.address !== business?.address) updates.address = formData.address || null;
      if (formData.subscription_tier !== business?.subscription_tier)
        updates.subscription_tier = formData.subscription_tier || null;
      if (formData.subscription_status !== business?.subscription_status)
        updates.subscription_status = formData.subscription_status || null;
      if (formData.is_active !== business?.is_active) updates.is_active = formData.is_active;

      onSubmit(updates);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              {mode === 'create' ? 'Create New Business' : 'Edit Business'}
            </h3>
          </div>

          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
                <input
                  type="text"
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="example.com"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry
                </label>
                <input
                  type="text"
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Size
                </label>
                <select
                  value={formData.size}
                  onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="201-500">201-500 employees</option>
                  <option value="501+">501+ employees</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Email
                </label>
                <input
                  type="email"
                  value={formData.contact_email}
                  onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  value={formData.contact_phone}
                  onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
              <textarea
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subscription Tier
                </label>
                <select
                  value={formData.subscription_tier}
                  onChange={(e) =>
                    setFormData({ ...formData, subscription_tier: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select tier</option>
                  <option value="Starter">Starter</option>
                  <option value="Professional">Professional</option>
                  <option value="Enterprise">Enterprise</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subscription Status
                </label>
                <select
                  value={formData.subscription_status}
                  onChange={(e) =>
                    setFormData({ ...formData, subscription_status: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select status</option>
                  <option value="Trial">Trial</option>
                  <option value="Active">Active</option>
                  <option value="Suspended">Suspended</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                Active
              </label>
            </div>
          </div>

          <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {isSubmitting
                ? 'Saving...'
                : mode === 'create'
                ? 'Create Business'
                : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
