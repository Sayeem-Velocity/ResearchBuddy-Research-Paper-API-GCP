import { Link } from 'react-router-dom';
import { Search, Sparkles, Zap, Brain, ArrowRight, BookOpen, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

const HomePage = () => {
  const features = [
    {
      icon: <Search className="w-8 h-8" />,
      title: "Multi-Source Search",
      description: "Search across arXiv, PubMed, Google Scholar, and IEEE Xplore simultaneously"
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "AI-Powered Analysis",
      description: "Get comprehensive summaries, strengths, and weaknesses using advanced AI"
    },
    {
      icon: <Sparkles className="w-8 h-8" />,
      title: "Interactive Chat",
      description: "Ask questions about papers and get instant, intelligent responses"
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Fast & Efficient",
      description: "Lightning-fast search and analysis powered by cutting-edge technology"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative overflow-hidden"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center space-x-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full mb-6"
            >
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-semibold">AI-Powered Research Assistant</span>
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-5xl md:text-7xl font-extrabold mb-6 bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 bg-clip-text text-transparent leading-tight"
            >
              Research Papers,
              <br />
              Simplified.
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto"
            >
              Search, analyze, and understand research papers with the power of AI.
              Get instant insights from multiple academic sources.
            </motion.p>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link 
                to="/search" 
                className="group flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 shadow-xl hover:shadow-2xl hover:scale-105"
              >
                <Search className="w-6 h-6" />
                <span>Start Searching</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <a 
                href="http://127.0.0.1:8004/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center space-x-2 bg-white hover:bg-gray-50 text-gray-700 px-8 py-4 rounded-xl text-lg font-semibold border-2 border-gray-300 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                <BookOpen className="w-6 h-6" />
                <span>API Docs</span>
              </a>
            </motion.div>
          </div>

          {/* Floating elements decoration */}
          <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-primary-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
        </div>
      </motion.div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900">
            Why Choose ResearchBuddy?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Powerful features designed to accelerate your research workflow
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              whileHover={{ y: -5 }}
              className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100"
            >
              <div className="bg-gradient-to-br from-primary-500 to-purple-600 text-white p-4 rounded-xl inline-block mb-6">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gradient-to-r from-primary-600 to-purple-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 text-center text-white">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
            >
              <div className="flex items-center justify-center mb-2">
                <TrendingUp className="w-8 h-8 mr-2" />
                <div className="text-5xl font-bold">4+</div>
              </div>
              <div className="text-xl text-primary-100">Data Sources</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <div className="flex items-center justify-center mb-2">
                <Sparkles className="w-8 h-8 mr-2" />
                <div className="text-5xl font-bold">AI</div>
              </div>
              <div className="text-xl text-primary-100">Powered Analysis</div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <div className="flex items-center justify-center mb-2">
                <Zap className="w-8 h-8 mr-2" />
                <div className="text-5xl font-bold">Fast</div>
              </div>
              <div className="text-xl text-primary-100">Lightning Speed</div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-primary-500 to-purple-600 rounded-3xl p-12 md:p-16 text-center text-white shadow-2xl"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Supercharge Your Research?
          </h2>
          <p className="text-xl mb-8 text-primary-100 max-w-2xl mx-auto">
            Start searching and analyzing research papers with AI assistance today.
          </p>
          <Link 
            to="/search"
            className="inline-flex items-center space-x-2 bg-white text-primary-600 px-8 py-4 rounded-xl text-lg font-bold hover:bg-gray-100 transition-all duration-300 shadow-xl hover:shadow-2xl hover:scale-105"
          >
            <Search className="w-6 h-6" />
            <span>Get Started Now</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </motion.div>
      </div>
    </div>
  );
};

export default HomePage;
