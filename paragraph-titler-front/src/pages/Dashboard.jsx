import { useState } from 'react';
import { paragraphAPI } from '../services/api';

const Dashboard = () => {
  const [paragraph, setParagraph] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleGenerate = async () => {
    if (!paragraph.trim()) {
      setError('Please enter a paragraph');
      return;
    }

    setError('');
    setLoading(true);
    setSuccess(false);

    try {
      const response = await paragraphAPI.generateTitle(paragraph);
      
      // Backend returns: { success: true, data: { title, paragraph, ... }, message: "..." }
      if (response.success && response.data) {
        const generatedTitle = response.data.title;
        setTitle(generatedTitle);
        setSuccess(true);
        // Optionally clear the paragraph after successful generation
        // setParagraph('');
      } else {
        setError(response.message || response.detail || 'Failed to generate title');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setParagraph('');
    setTitle('');
    setError('');
    setSuccess(false);
  };

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Generate Your Title
          </h1>
          <p className="text-gray-600 text-lg">
            Paste your paragraph below and let AI create the perfect title
          </p>
        </div>

        <div className="space-y-6">
          {/* Input Section */}
          <div className="card animate-slide-up">
            <label htmlFor="paragraph" className="block text-sm font-semibold text-gray-700 mb-3">
              Your Paragraph
            </label>
            <textarea
              id="paragraph"
              value={paragraph}
              onChange={(e) => setParagraph(e.target.value)}
              rows={8}
              className="input-field resize-none"
              placeholder="Enter your paragraph here..."
            />
            <div className="flex justify-between items-center mt-4">
              <span className="text-sm text-gray-500">
                {paragraph.length} characters
              </span>
              <div className="space-x-3">
                <button
                  onClick={handleClear}
                  className="btn-secondary text-sm py-2 px-4"
                  disabled={loading}
                >
                  Clear
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={loading || !paragraph.trim()}
                  className="btn-primary text-sm py-2 px-4"
                >
                  {loading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating...
                    </span>
                  ) : (
                    'Generate Title'
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg animate-slide-down">
              {error}
            </div>
          )}

          {/* Result Section */}
          {title && (
            <div className="card animate-slide-up">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-800">Generated Title</h2>
                {success && (
                  <span className="text-green-600 font-semibold flex items-center">
                    <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Success!
                  </span>
                )}
              </div>
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border-2 border-indigo-200">
                <p className="text-2xl md:text-3xl font-bold text-gray-800 text-center">
                  {title}
                </p>
              </div>
            </div>
          )}

          {/* Info Card */}
          {!title && !loading && (
            <div className="card bg-indigo-50 border-2 border-indigo-200 animate-fade-in">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">💡</div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">Tips for Best Results</h3>
                  <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                    <li>Provide a complete paragraph with clear context</li>
                    <li>The longer and more detailed the paragraph, the better the title</li>
                    <li>Make sure your paragraph has a clear main idea</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

