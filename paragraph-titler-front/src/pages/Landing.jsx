import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Landing = () => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return null; // Will redirect via App.jsx
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center px-4 py-20">
        <div className="max-w-4xl mx-auto text-center animate-fade-in">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-slide-down">
            Paragraph Titler
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 animate-slide-up">
            Transform your paragraphs into compelling titles with the power of AI
          </p>
          <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto">
            Simply paste your paragraph, and our advanced AI model will generate the perfect title for you. 
            Save your work, track your history, and enhance your writing effortlessly.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-slide-up">
            <Link to="/register" className="btn-primary text-lg px-8 py-4">
              Get Started Free
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-4">
              Sign In
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
            Why Choose Paragraph Titler?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center transform hover:scale-105">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">AI-Powered</h3>
              <p className="text-gray-600">
                Advanced machine learning models trained to understand context and generate meaningful titles
              </p>
            </div>
            <div className="card text-center transform hover:scale-105">
              <div className="text-4xl mb-4">📚</div>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">History Tracking</h3>
              <p className="text-gray-600">
                Keep track of all your generated titles and paragraphs in one convenient place
              </p>
            </div>
            <div className="card text-center transform hover:scale-105">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">Lightning Fast</h3>
              <p className="text-gray-600">
                Get your titles generated in seconds with our optimized API infrastructure
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-gray-400">© 2024 Paragraph Titler. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;

