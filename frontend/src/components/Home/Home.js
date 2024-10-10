// src/components/Home/Home.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Alert } from 'react-bootstrap';
import { datasetService, getErrorMessage } from '../../services/api';
import PageLoading from '../ui/PageLoading';

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
      <div className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Available Datasets</h1>
        <Alert variant="info">
          No datasets are returned from the API yet. Ensure the backend is running and the
          study catalog is populated.
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Available Datasets</h1>
        <p className="mt-2 max-w-2xl text-slate-600">
          Browse studies by cancer type and open a study for summary, clinical data, analysis,
          and heatmaps.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
      {groups.map(([type, datasets]) => (
        <section key={type} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <h2 className="mb-3 text-lg font-semibold text-slate-800">{type}</h2>
          <ul className="space-y-2">
            {datasets.map((dataset) => (
              <li key={dataset.id}>
                <Link
                  to={`/datasets/${dataset.id}`}
                  className="block rounded-lg border border-slate-200 px-3 py-2 text-slate-700 transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-800"
                >
                  <div className="font-medium">{dataset.name}</div>
                  <div className="text-xs text-slate-400">{dataset.id}</div>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
      </div>
    </div>
  );
};

export default Home;
