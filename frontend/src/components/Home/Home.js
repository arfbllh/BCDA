// src/components/Home/Home.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Alert } from 'react-bootstrap';
import { datasetService, getErrorMessage } from '../../services/api';
import PageLoading from '../ui/PageLoading';
import './Home.css';

const Home = () => {
  const [groupedDatasets, setGroupedDatasets] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const fetchDatasets = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await datasetService.getAllDatasets();
        if (!cancelled) {
          setGroupedDatasets(data || {});
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err, 'Failed to fetch datasets'));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchDatasets();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <PageLoading message="Loading datasets…" />;
  }
  if (error) {
    return (
      <Alert variant="danger" className="mt-3" role="alert">
        {error}
      </Alert>
    );
  }

  const groups = Object.entries(groupedDatasets).filter(
    ([, list]) => Array.isArray(list) && list.length > 0
  );

  if (groups.length === 0) {
    return (
      <div className="home-container">
        <h1 className="h2 mb-3">Available Datasets</h1>
        <Alert variant="info">
          No datasets are returned from the API yet. Ensure the backend is running and the
          study catalog is populated.
        </Alert>
      </div>
    );
  }

  return (
    <div className="home-container">
      <h1 className="home-title">Available Datasets</h1>
      <p className="home-lead text-muted">
        Browse studies by cancer type and open a study for summary, clinical data, analysis,
        and heatmaps.
      </p>

      <div className="datasets-card">
        {groups.map(([type, datasets]) => (
          <div key={type} className="dataset-section">
            <h2 className="h4">{type}</h2>
            <ul className="dataset-list">
              {datasets.map((dataset) => (
                <li key={dataset.id} className="dataset-item">
                  <Link to={`/datasets/${dataset.id}`} className="dataset-link">
                    <div className="dataset-name">{dataset.name}</div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Home;
