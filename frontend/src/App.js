import React, { useState } from 'react';
import Companies from "./Companies";
import AnnualReportAnalyzer from "./AnnualReportAnalyzer";
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('companies'); // 'companies' or 'reports'

  return (
    <div className="App">
      <header className="app-header">
        <h1>AI Finance Agent</h1>
        <nav className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'companies' ? 'active' : ''}`}
            onClick={() => setActiveTab('companies')}
          >
            Company Data
          </button>
          <button 
            className={`nav-tab ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            Annual Report Analysis
          </button>
        </nav>
      </header>
      
      <main className="app-main">
        {activeTab === 'companies' ? (
          <Companies />
        ) : (
          <AnnualReportAnalyzer />
        )}
      </main>
    </div>
  );
}

export default App;