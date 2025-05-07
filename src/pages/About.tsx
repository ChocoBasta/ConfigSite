import React from 'react';
import '../styles/About.css';

const About: React.FC = () => {
  return (
    <div className="about">
      <section className="about-content">
        <h1>About ConfigSite</h1>
        <p>
          ConfigSite is a modern web application built with React and TypeScript.
          It provides a solid foundation for building scalable and maintainable web applications.
        </p>
        
        <h2>Our Mission</h2>
        <p>
          To provide developers with a robust and flexible platform for creating
          modern web applications with best practices and modern technologies.
        </p>

        <h2>Technology Stack</h2>
        <ul>
          <li>React 18</li>
          <li>TypeScript</li>
          <li>CSS Modules</li>
          <li>React Router</li>
        </ul>
      </section>
    </div>
  );
};

export default About; 