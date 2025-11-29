import { useState, useEffect } from 'react';
import { paragraphAPI } from '../services/api';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await paragraphAPI.getHistory();
      
      // Backend returns: { success: true, data: [...], total_results: N, message: "..." }
      if (response.success && Array.isArray(response.data)) {
        setHistory(response.data);
      } else if (Array.isArray(response.data)) {
        setHistory(response.data);
      } else {
        setHistory([]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.message || 'Failed to load history');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Your History
          </h1>
          <p className="text-gray-600 text-lg">
            All your generated titles in one place
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg animate-slide-down">
            {error}
          </div>
        )}

        {history.length === 0 ? (
          <div className="card text-center py-12 animate-fade-in">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-2xl font-semibold text-gray-800 mb-2">No History Yet</h3>
            <p className="text-gray-600 mb-6">
              Start generating titles to see them appear here
            </p>
            <a
              href="/dashboard"
              className="btn-primary inline-block"
            >
              Generate Your First Title
            </a>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {history.map((item, index) => (
              <div
                key={item.result_id || item.id || index}
                className="card hover:scale-105 transition-transform duration-300 animate-slide-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-indigo-600 mb-2 line-clamp-2">
                    {item.generated_title || item.title || 'Untitled'}
                  </h3>
                  <p className="text-xs text-gray-500 mb-3">
                    {formatDate(item.created_at || item.date || item.timestamp)}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-700 line-clamp-4">
                    {item.paragraph || 'No paragraph available'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;

