import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const AnnualReportAnalyzer = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [modelInfo, setModelInfo] = useState(null);
  const [stats, setStats] = useState(null);
  const [companyName, setCompanyName] = useState('');

  // Load initial data
  useEffect(() => {
    fetchUploadedFiles();
    fetchModelInfo();
    fetchStats();
  }, []);

  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/uploaded-files`);
      if (response.ok) {
        const files = await response.json();
        setUploadedFiles(files);
        if (files.length > 0 && !selectedFile) {
          setSelectedFile(files[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching uploaded files:', error);
    }
  };

  const fetchModelInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/model-info`);
      if (response.ok) {
        const info = await response.json();
        setModelInfo(info);
      }
    } catch (error) {
      console.error('Error fetching model info:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (response.ok) {
        const statsData = await response.json();
        setStats(statsData);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setStatus({ type: 'error', message: 'Please select a PDF file.' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'info', message: 'Uploading file...' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setStatus({ type: 'success', message: `File uploaded successfully: ${result.filename}` });
        fetchUploadedFiles(); // Refresh file list
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `Upload failed: ${error.detail}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `Upload failed: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const processReport = async (filename) => {
    setLoading(true);
    setStatus({ type: 'info', message: 'Processing report...' });

    try {
      const response = await fetch(`${API_BASE_URL}/process-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pdf_filename: filename,
          force_reprocess: false,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setStatus({ 
          type: 'success', 
          message: `Report processed successfully! Found ${result.total_chunks} chunks and ${Object.keys(result.financial_data).length} financial metrics.` 
        });
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `Processing failed: ${error.detail}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `Processing failed: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const batchProcessReports = async () => {
    setLoading(true);
    setStatus({ type: 'info', message: 'Processing all reports...' });

    try {
      const response = await fetch(`${API_BASE_URL}/batch-process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          force_reprocess: false,
        }),
      });

      if (response.ok) {
        const results = await response.json();
        const successCount = results.filter(r => r.success).length;
        setStatus({ 
          type: 'success', 
          message: `Batch processing completed! Successfully processed ${successCount}/${results.length} reports.` 
        });
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `Batch processing failed: ${error.detail}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `Batch processing failed: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!selectedFile || !query.trim()) {
      setStatus({ type: 'error', message: 'Please select a file and enter a question.' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'info', message: 'Analyzing report with FinAgent...' });

    try {
      const response = await fetch(`${API_BASE_URL}/query-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pdf_filename: selectedFile,
          query: query,
          company_name: companyName || undefined,
          force_reprocess: false,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setResponse(result.response);
          setStatus({ type: 'success', message: 'Analysis completed successfully!' });
        } else {
          setStatus({ type: 'error', message: `Analysis failed: ${result.error}` });
        }
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `Analysis failed: ${error.detail}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `Analysis failed: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const deleteFile = async (filename) => {
    try {
      const response = await fetch(`${API_BASE_URL}/uploaded-files/${filename}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setStatus({ type: 'success', message: `File ${filename} deleted successfully.` });
        fetchUploadedFiles(); // Refresh file list
        if (selectedFile === filename) {
          setSelectedFile('');
        }
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `Delete failed: ${error.detail}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `Delete failed: ${error.message}` });
    }
  };

  const testFinAgent = async () => {
    setLoading(true);
    setStatus({ type: 'info', message: 'Testing FinAgent model...' });

    try {
      const response = await fetch(`${API_BASE_URL}/test-finagent`, {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setStatus({ type: 'success', message: 'FinAgent test successful! Model is working correctly.' });
          setResponse(result.response);
        } else {
          setStatus({ type: 'error', message: `FinAgent test failed: ${result.response}` });
        }
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `FinAgent test failed: ${error.detail}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `FinAgent test failed: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-analyzer">
      <h2>Annual Report Analysis with FinAgent</h2>
      
      {/* Model Information */}
      {modelInfo && (
        <div className="model-info">
          <h4>FinAgent Model Status</h4>
          <p><strong>Base Model:</strong> {modelInfo.base_model}</p>
          <p><strong>Adapter Type:</strong> {modelInfo.adapter_type}</p>
          <p><strong>Device:</strong> {modelInfo.device}</p>
          <p><strong>Status:</strong> {modelInfo.status}</p>
          <button 
            className="process-button" 
            onClick={testFinAgent}
            disabled={loading}
          >
            {loading ? <span className="loading"></span> : 'Test FinAgent'}
          </button>
        </div>
      )}

      {/* Statistics */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_processed_files}</div>
            <div className="stat-label">Processed Files</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.conversation_history_length}</div>
            <div className="stat-label">Conversations</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.llm_available ? '✓' : '✗'}</div>
            <div className="stat-label">Model Available</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.llm_client_type}</div>
            <div className="stat-label">LLM Type</div>
          </div>
        </div>
      )}

      {/* Status Messages */}
      {status.message && (
        <div className={`status-message status-${status.type}`}>
          {status.message}
        </div>
      )}

      {/* File Upload Section */}
      <div className="upload-section">
        <h3>Upload Annual Report</h3>
        <p>Upload a PDF file to analyze with FinAgent</p>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          className="file-input"
          id="file-upload"
          disabled={loading}
        />
        <label htmlFor="file-upload" className="upload-button">
          {loading ? <span className="loading"></span> : 'Choose PDF File'}
        </label>
        
        {uploadedFiles.length > 0 && (
          <div className="file-list">
            <h4>Uploaded Files</h4>
            {uploadedFiles.map((filename) => (
              <div key={filename} className="file-item">
                <span>{filename}</span>
                <div>
                  <button
                    className="process-button"
                    onClick={() => processReport(filename)}
                    disabled={loading}
                  >
                    Process
                  </button>
                  <button
                    className="delete-button"
                    onClick={() => deleteFile(filename)}
                    disabled={loading}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            <button
              className="process-button"
              onClick={batchProcessReports}
              disabled={loading}
            >
              {loading ? <span className="loading"></span> : 'Process All Files'}
            </button>
          </div>
        )}
      </div>

      {/* Query Section */}
      <div className="query-section">
        <h3>Ask FinAgent</h3>
        <p>Ask questions about the uploaded annual reports</p>
        
        <select
          value={selectedFile}
          onChange={(e) => setSelectedFile(e.target.value)}
          disabled={uploadedFiles.length === 0 || loading}
        >
          <option value="">Select a file to analyze</option>
          {uploadedFiles.map((filename) => (
            <option key={filename} value={filename}>
              {filename}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Enter company name (optional)"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          className="query-input"
          disabled={loading}
        />

        <textarea
          placeholder="Ask FinAgent about the annual report... (e.g., 'What was the company's revenue growth?', 'What are the main risk factors?', 'How did they perform in international markets?')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="query-input"
          rows="4"
          disabled={loading}
        />

        <button
          className="ask-button"
          onClick={askQuestion}
          disabled={!selectedFile || !query.trim() || loading}
        >
          {loading ? <span className="loading"></span> : 'Ask FinAgent'}
        </button>
      </div>

      {/* Response Section */}
      {response && (
        <div className="response-section">
          <h3>FinAgent Analysis</h3>
          <div className="response-content">
            {response}
          </div>
        </div>
      )}

      {/* Sample Questions */}
      <div className="query-section">
        <h3>Sample Questions</h3>
        <p>Try these questions to get started:</p>
        <ul style={{ textAlign: 'left', lineHeight: '1.8' }}>
          <li><strong>Financial Performance:</strong> "What was the company's revenue and profit performance?"</li>
          <li><strong>Market Analysis:</strong> "How did the company perform in international markets?"</li>
          <li><strong>Risk Assessment:</strong> "What are the main risk factors mentioned in the report?"</li>
          <li><strong>Strategy:</strong> "What are the key strategic initiatives for the coming year?"</li>
          <li><strong>Growth:</strong> "What were the main drivers of revenue growth?"</li>
          <li><strong>ESG:</strong> "What ESG initiatives were highlighted in the report?"</li>
        </ul>
      </div>
    </div>
  );
};

export default AnnualReportAnalyzer; 