/**
 * Header Component
 * Top navigation bar with user actions and status
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Fetch API health status
  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.health();
      return response.data;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    }

    if (isUserMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isUserMenuOpen]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Get display name: prioritize full_name, fallback to username
  const displayName = user?.full_name || user?.username || 'User';

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Page title / breadcrumb - will be populated by child pages */}
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-semibold text-gray-900">
            {/* This will be set by individual pages */}
          </h2>
        </div>

        {/* Right side - Status and user actions */}
        <div className="flex items-center gap-6">
          {/* API Status Indicator */}
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                healthData?.status === 'healthy'
                  ? 'bg-green-500'
                  : 'bg-red-500'
              }`}
              title={healthData?.status === 'healthy' ? 'API Online' : 'API Offline'}
            />
            <span className="text-sm text-gray-600">
              {healthData?.status === 'healthy' ? 'Online' : 'Offline'}
            </span>
          </div>

          {/* Notifications - placeholder for future */}
          <button
            className="relative p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
            title="Notifications"
          >
            <span className="text-xl">🔔</span>
            {/* Badge for unread notifications */}
            {false && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            )}
          </button>

          {/* User menu with dropdown */}
          <div className="relative" ref={menuRef}>
            <button
              className="flex items-center gap-2 px-3 py-2 text-gray-700 hover:text-gray-900 rounded-lg hover:bg-gray-100"
              title="User menu"
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            >
              <span className="text-xl">👤</span>
              <span className="text-sm font-medium">{displayName}</span>
              <svg
                className={`w-4 h-4 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown menu */}
            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                {/* User info section */}
                <div className="px-4 py-3 border-b border-gray-200">
                  <p className="text-sm font-medium text-gray-900">{displayName}</p>
                  <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
                  {user?.role && (
                    <p className="text-xs text-gray-400 mt-1 capitalize">
                      {user.role.replace('_', ' ')}
                    </p>
                  )}
                </div>

                {/* Menu items */}
                <button
                  onClick={() => {
                    setIsUserMenuOpen(false);
                    navigate('/settings');
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                >
                  <span>⚙️</span>
                  Settings
                </button>

                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                >
                  <span>🚪</span>
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
