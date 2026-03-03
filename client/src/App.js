import { useState } from 'react';
import './App.css';

const API_URL = 'https://uc5501ey95.execute-api.eu-central-1.amazonaws.com/check';

function App() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch(`${API_URL}?url=${encodeURIComponent(url.trim())}`);
      const data = await res.json();

      if (data.error && !data.status_code) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError('Could not reach the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1 className="title">AmIDown?</h1>
      <p className="subtitle">Check if a website is up or down</p>

      <form className="search-bar" onSubmit={handleCheck}>
        <input
          id="url-input"
          type="text"
          placeholder="Enter a URL — e.g. google.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          autoFocus
        />
        <button id="check-btn" type="submit" disabled={loading}>
          {loading ? '...' : 'Check'}
        </button>
      </form>

      {loading && <div className="loader" />}

      {error && <p className="error-msg">{error}</p>}

      {result && (
        <div className="result-card">
          <div className="result-header">
            <span className={`status-dot ${result.is_up ? 'up' : 'down'}`} />
            <span className="result-url">{result.url}</span>
          </div>
          <div className={`result-status ${result.is_up ? 'up' : 'down'}`}>
            {result.is_up ? 'It\'s up!' : 'It\'s down.'}
          </div>
          {result.warning && (
            <div className="result-warning">⚠️ {result.warning}</div>
          )}
          <div className="result-details">
            {result.status_code && (
              <div className="detail">
                <span className="detail-label">Status</span>
                <span className="detail-value">{result.status_code}</span>
              </div>
            )}
            {result.latency_ms != null && (
              <div className="detail">
                <span className="detail-label">Latency</span>
                <span className="detail-value">{result.latency_ms} ms</span>
              </div>
            )}
            {result.region && (
              <div className="detail">
                <span className="detail-label">Region</span>
                <span className="detail-value">{result.region}</span>
              </div>
            )}
            {result.error && (
              <div className="detail">
                <span className="detail-label">Error</span>
                <span className="detail-value">{result.error}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
