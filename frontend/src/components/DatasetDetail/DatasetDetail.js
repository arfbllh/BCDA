// src/components/DatasetDetail/DatasetDetail.js
import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Alert } from 'react-bootstrap';
import { datasetService, getErrorMessage } from '../../services/api';
import Summary from '../Summary/Summary';
import ClinicalData from '../ClinicalData/ClinicalData';
import Analysis from '../Analysis/Analysis';
import Heatmap from '../Heatmap/Heatmap';
import PageLoading from '../ui/PageLoading';
import './DatasetDetail.css';

const TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'clinical', label: 'Clinical Data' },
  { id: 'analysis', label: 'Analysis' },
  { id: 'heatmap', label: 'Heatmap' },
];

const DatasetDetail = () => {
  const { datasetId } = useParams();
  const [dataset, setDataset] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      setDataset(null);
      try {
        const meta = await datasetService.getDatasetMeta(datasetId);
        if (cancelled) return;
        if (!meta) {
          setError(null);
          setDataset(null);
        } else {
          setDataset(meta);
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err, 'Failed to load datasets'));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  if (loading) {
    return <PageLoading message="Loading study…" />;
  }
  if (error) {
    return (
      <Alert variant="danger" className="mt-3" role="alert">
        {error}
      </Alert>
    );
  }
  if (!dataset) {
    return (
      <Alert variant="warning" className="mt-3" role="alert">
        <Alert.Heading className="h5">Dataset not found</Alert.Heading>
        <p className="mb-0">
          No study matches <code>{datasetId}</code> in the catalog.
        </p>
      </Alert>
    );
  }

  return (
    <div className="dataset-detail">
      <Link to="/" className="back-link">
        ← All datasets
      </Link>
      <h1 className="dataset-title">{dataset.name}</h1>
      <p className="dataset-type text-muted">{dataset.type}</p>

      <div
        className="tabs"
        role="tablist"
        aria-label="Study sections"
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            className={activeTab === tab.id ? 'active' : ''}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'summary' && (
          <div
            role="tabpanel"
            id="panel-summary"
            aria-labelledby="tab-summary"
          >
            <Summary datasetId={datasetId} />
          </div>
        )}
        {activeTab === 'clinical' && (
          <div
            role="tabpanel"
            id="panel-clinical"
            aria-labelledby="tab-clinical"
          >
            <ClinicalData datasetId={datasetId} />
          </div>
        )}
        {activeTab === 'analysis' && (
          <div
            role="tabpanel"
            id="panel-analysis"
            aria-labelledby="tab-analysis"
          >
            <Analysis datasetId={datasetId} />
          </div>
        )}
        {activeTab === 'heatmap' && (
          <div
            role="tabpanel"
            id="panel-heatmap"
            aria-labelledby="tab-heatmap"
          >
            <Heatmap datasetId={datasetId} />
          </div>
        )}
      </div>
    </div>
  );
};

export default DatasetDetail;
