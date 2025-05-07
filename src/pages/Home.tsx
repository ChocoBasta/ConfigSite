import React from 'react';
import '../styles/Home.css';

const Home: React.FC = () => {
  return (
    <div className="home">
      <section className="hero">
        <h1>Welcome to ConfigSite</h1>
        <p>Your modern web application solution</p>
      </section>
      
      <section className="features">
        <h2>Features</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <h3>Modern Design</h3>
            <p>Clean and responsive interface</p>
          </div>
          <div className="feature-card">
            <h3>TypeScript</h3>
            <p>Type-safe development</p>
          </div>
          <div className="feature-card">
            <h3>React</h3>
            <p>Component-based architecture</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home; 