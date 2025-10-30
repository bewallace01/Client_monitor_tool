/**
 * Home Page - Landing page with API status
 */

import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

const Home = () => {
  const { data: rootData, isLoading: rootLoading } = useQuery({
    queryKey: ['root'],
    queryFn: async () => {
      const response = await api.root();
      return response.data;
    },
  });

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.health();
      return response.data;
    },
  });

  const { data: infoData, isLoading: infoLoading } = useQuery({
    queryKey: ['info'],
    queryFn: async () => {
      const response = await api.info();
      return response.data;
    },
  });

  const isLoading = rootLoading || healthLoading || infoLoading;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="max-w-2xl w-full mx-4">
        <div className="card">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {rootData?.name || 'Client Intelligence Monitor'}
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Version {rootData?.version || '2.0.0'}
          </p>

          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-gray-600">Connecting to API...</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="font-semibold text-green-900">API Status</span>
                </div>
                <span className="text-green-700">{healthData?.status || 'healthy'}</span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Environment</p>
                  <p className="font-semibold text-gray-900">
                    {infoData?.environment || 'development'}
                  </p>
                </div>
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">API Version</p>
                  <p className="font-semibold text-gray-900">
                    {infoData?.api_version || 'v1'}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-600 mb-3">Quick Links:</p>
                <div className="flex flex-wrap gap-2">
                  <a
                    href="http://localhost:8000/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-sm"
                  >
                    API Documentation
                  </a>
                  <a
                    href="http://localhost:8000/redoc"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-sm"
                  >
                    ReDoc
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 text-center text-gray-600 text-sm">
          <p>Backend API: <code className="bg-gray-200 px-2 py-1 rounded">http://localhost:8000</code></p>
          <p className="mt-2">Frontend: <code className="bg-gray-200 px-2 py-1 rounded">http://localhost:5173</code></p>
        </div>
      </div>
    </div>
  );
};

export default Home;
