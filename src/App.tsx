import React from 'react';
import { HashRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './styles/App.css';

// Import pages
import Home from './pages/Home';
import About from './pages/About';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>ConfigSite</h1>
          <nav>
            <Link to="/">Home</Link>
            <Link to="/about">About</Link>
          </nav>
        </header>
        
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>&copy; 2024 ConfigSite. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
};

export default App; 