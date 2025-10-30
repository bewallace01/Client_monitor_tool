/**
 * User Management Component
 * Manage users - create, edit, delete, assign roles and businesses
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-hot-toast';
import {
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  activateUser,
  deactivateUser,
  type User,
  type UserCreate,
  type UserUpdate,
} from '../../services/users';
import { getBusinesses } from '../../services/businesses';

export default function UserManagement() {
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [filters, setFilters] = useState({
    role: undefined as 'system_admin' | 'business_admin' | 'base_user' | undefined,
    is_active: undefined as boolean | undefined,
  });

  const isSystemAdmin = currentUser?.role === 'system_admin';
  const isBusinessAdmin = currentUser?.role === 'business_admin';

  // Query users based on role
  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['users', filters],
    queryFn: () =>
      getUsers({
        ...filters,
        // Business admins only see users in their business
        business_id: isBusinessAdmin ? currentUser?.business_id || undefined : undefined,
      }),
  });

  // Query businesses (for system admin)
  const { data: businessesData } = useQuery({
    queryKey: ['businesses'],
    queryFn: () => getBusinesses({}),
    enabled: isSystemAdmin,
  });

  // Create user mutation
  const createMutation = useMutation({
    mutationFn: (userData: UserCreate) => createUser(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User created successfully');
      setIsCreateModalOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    },
  });

  // Update user mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: UserUpdate }) =>
      updateUser(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User updated successfully');
      setIsEditModalOpen(false);
      setSelectedUser(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update user');
    },
  });

  // Delete user mutation
  const deleteMutation = useMutation({
    mutationFn: (userId: number) => deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    },
  });

  // Toggle active status mutation
  const toggleActiveMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: number; isActive: boolean }) =>
      isActive ? deactivateUser(userId) : activateUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User status updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update user status');
    },
  });

  const handleDeleteUser = (user: User) => {
    if (window.confirm(`Are you sure you want to delete user "${user.username}"?`)) {
      deleteMutation.mutate(user.id);
    }
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setIsEditModalOpen(true);
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'system_admin':
        return 'bg-purple-100 text-purple-800';
      case 'business_admin':
        return 'bg-blue-100 text-blue-800';
      case 'base_user':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'system_admin':
        return 'System Admin';
      case 'business_admin':
        return 'Business Admin';
      case 'base_user':
        return 'Base User';
      default:
        return role;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">User Management</h2>
            <p className="text-sm text-gray-600 mt-1">
              {isSystemAdmin
                ? 'Manage all users across all businesses'
                : 'Manage users in your business'}
            </p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add User
          </button>
        </div>

        {/* Filters */}
        <div className="mt-4 flex gap-4">
          <select
            value={filters.role || ''}
            onChange={(e) =>
              setFilters({
                ...filters,
                role: e.target.value
                  ? (e.target.value as 'system_admin' | 'business_admin' | 'base_user')
                  : undefined,
              })
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Roles</option>
            {isSystemAdmin && <option value="system_admin">System Admin</option>}
            <option value="business_admin">Business Admin</option>
            <option value="base_user">Base User</option>
          </select>

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
        </div>
      </div>

      {/* User List */}
      <div className="overflow-x-auto">
        {usersLoading ? (
          <div className="p-8 text-center text-gray-500">Loading users...</div>
        ) : !usersData?.items.length ? (
          <div className="p-8 text-center text-gray-500">No users found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                {isSystemAdmin && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Business
                  </th>
                )}
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usersData?.items.map((user) => {
                const business = businessesData?.items.find((b) => b.id === user.business_id);
                return (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="font-medium text-gray-900">{user.username}</div>
                        {user.full_name && (
                          <div className="text-sm text-gray-500">{user.full_name}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(
                          user.role
                        )}`}
                      >
                        {getRoleLabel(user.role)}
                      </span>
                    </td>
                    {isSystemAdmin && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {business?.name || (user.business_id ? 'Unknown' : '-')}
                      </td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() =>
                          toggleActiveMutation.mutate({
                            userId: user.id,
                            isActive: user.is_active,
                          })
                        }
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleEditUser(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user)}
                        className="text-red-600 hover:text-red-900"
                        disabled={user.id === currentUser?.id}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {usersData && usersData.total_pages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {usersData.items.length} of {usersData.total} users
          </div>
          <div className="text-sm text-gray-600">
            Page {usersData.page} of {usersData.total_pages}
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {isCreateModalOpen && (
        <UserFormModal
          mode="create"
          businesses={businessesData?.items || []}
          isSystemAdmin={isSystemAdmin}
          currentUserBusinessId={currentUser?.business_id || null}
          onSubmit={(data) => createMutation.mutate(data)}
          onClose={() => setIsCreateModalOpen(false)}
          isSubmitting={createMutation.isPending}
        />
      )}

      {/* Edit User Modal */}
      {isEditModalOpen && selectedUser && (
        <UserFormModal
          mode="edit"
          user={selectedUser}
          businesses={businessesData?.items || []}
          isSystemAdmin={isSystemAdmin}
          currentUserBusinessId={currentUser?.business_id || null}
          onSubmit={(data) => updateMutation.mutate({ id: selectedUser.id, updates: data })}
          onClose={() => {
            setIsEditModalOpen(false);
            setSelectedUser(null);
          }}
          isSubmitting={updateMutation.isPending}
        />
      )}
    </div>
  );
}

// User Form Modal Component
interface UserFormModalProps {
  mode: 'create' | 'edit';
  user?: User;
  businesses: any[];
  isSystemAdmin: boolean;
  currentUserBusinessId: string | null;
  onSubmit: (data: UserCreate | UserUpdate) => void;
  onClose: () => void;
  isSubmitting: boolean;
}

function UserFormModal({
  mode,
  user,
  businesses,
  isSystemAdmin,
  currentUserBusinessId,
  onSubmit,
  onClose,
  isSubmitting,
}: UserFormModalProps) {
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    full_name: user?.full_name || '',
    password: '',
    role: user?.role || ('base_user' as 'system_admin' | 'business_admin' | 'base_user'),
    business_id: user?.business_id || currentUserBusinessId || '',
    is_active: user?.is_active !== undefined ? user.is_active : true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === 'create') {
      // For create, all fields including password
      onSubmit({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || null,
        role: formData.role,
        business_id: formData.business_id || null,
        is_active: formData.is_active,
      });
    } else {
      // For edit, only include changed fields
      const updates: UserUpdate = {};
      if (formData.username !== user?.username) updates.username = formData.username;
      if (formData.email !== user?.email) updates.email = formData.email;
      if (formData.full_name !== user?.full_name) updates.full_name = formData.full_name || null;
      if (formData.password) updates.password = formData.password;
      if (formData.role !== user?.role) updates.role = formData.role;
      if (formData.business_id !== user?.business_id) updates.business_id = formData.business_id || null;
      if (formData.is_active !== user?.is_active) updates.is_active = formData.is_active;

      onSubmit(updates);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              {mode === 'create' ? 'Create New User' : 'Edit User'}
            </h3>
          </div>

          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username *
              </label>
              <input
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password {mode === 'create' ? '*' : '(leave blank to keep current)'}
              </label>
              <input
                type="password"
                required={mode === 'create'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
              <select
                required
                value={formData.role}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    role: e.target.value as 'system_admin' | 'business_admin' | 'base_user',
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {isSystemAdmin && <option value="system_admin">System Admin</option>}
                <option value="business_admin">Business Admin</option>
                <option value="base_user">Base User</option>
              </select>
            </div>

            {isSystemAdmin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business
                </label>
                <select
                  value={formData.business_id}
                  onChange={(e) => setFormData({ ...formData, business_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">No Business (System Admin only)</option>
                  {businesses.map((business) => (
                    <option key={business.id} value={business.id}>
                      {business.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

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
              {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create User' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
