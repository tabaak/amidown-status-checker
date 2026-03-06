import { useState } from 'react';
import './App.css';

const API_URL = {
  frankfurt: 'https://tyfrfcxfp5.execute-api.eu-central-1.amazonaws.com/prod/check',
  singapore: 'https://3643dmk2aj.execute-api.ap-southeast-1.amazonaws.com/prod/check',
  virginia: 'https://qqir65hwzl.execute-api.us-east-1.amazonaws.com/prod/check',
}

function App() {
  const [url, setUrl] = useState('');
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setResults({});
    setError(null);

    try {
      const entries = Object.entries(API_URL);
      const responses = await Promise.allSettled(
        entries.map(([, endpoint]) =>
          fetch(`${endpoint}?url=${encodeURIComponent(url.trim())}`).then((r) => r.json())
        )
      );

      const newResults = {};
      let allErrored = true;

      entries.forEach(([region], i) => {
        const res = responses[i];
        if (res.status === 'fulfilled') {
          newResults[region] = res.value;
          if (!(res.value.error && !res.value.status_code)) {
            allErrored = false;
          }
        } else {
          newResults[region] = { error: 'Could not reach this region.' };
        }
      });

      if (allErrored && Object.values(newResults).every((r) => r.error && !r.status_code)) {
        setError(Object.values(newResults)[0].error);
      } else {
        setResults(newResults);
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

      {Object.keys(results).length > 0 && (
        <div className="results-row">
          {Object.entries(results).map(([region, result]) => (
            <div className="result-card" key={region}>
              <div className="result-header">
                <span className={`status-dot ${result.is_up ? 'up' : 'down'}`} />
                <span className="result-url">{result.url}</span>
                <span className="result-region-badge">{region}</span>
              </div>
              <div className={`result-status ${result.is_up ? 'up' : 'down'}`}>
                {result.is_up ? "It's up!" : "It's down."}
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
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
