// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home/Home';
import DatasetDetail from './components/DatasetDetail/DatasetDetail';
import About from './components/pages/About';
import Help from './components/pages/Help';
import JobsPage from './components/pages/JobsPage';
import ApiDocsPage from './components/pages/ApiDocsPage';
import Navbar from './components/Navbar/Navbar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/datasets/:datasetId" element={<DatasetDetail />} />
            <Route path="/about" element={<About />} />
            <Route path="/help" element={<Help />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/api-docs" element={<ApiDocsPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;