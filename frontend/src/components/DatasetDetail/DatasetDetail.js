// src/components/DatasetDetail/DatasetDetail.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { datasetService, getErrorMessage } from '../../services/api';
import Summary from '../Summary/Summary';
import ClinicalData from '../ClinicalData/ClinicalData';
import Analysis from '../Analysis/Analysis';
import Heatmap from '../Heatmap/Heatmap';
import './DatasetDetail.css';

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

  if (loading) return <div className="loading">Loading dataset details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!dataset) {
    return (
      <div className="error">
        <p>Dataset not found.</p>
        <p>No study matches &quot;{datasetId}&quot; in the catalog.</p>
      </div>
    );
  }

  return (
    <div className="dataset-detail">
      <h1>{dataset.name}</h1>
      <p className="dataset-type">{dataset.type}</p>

      <div className="tabs">
        <button 
          className={activeTab === 'summary' ? 'active' : ''} 
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={activeTab === 'clinical' ? 'active' : ''} 
          onClick={() => setActiveTab('clinical')}
        >
          Clinical Data
        </button>
        <button 
          className={activeTab === 'analysis' ? 'active' : ''} 
          onClick={() => setActiveTab('analysis')}
        >
          Analysis
        </button>
        <button 
          className={activeTab === 'heatmap' ? 'active' : ''} 
          onClick={() => setActiveTab('heatmap')}
        >
          Heatmap
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'summary' && <Summary datasetId={datasetId} />}
        {activeTab === 'clinical' && <ClinicalData datasetId={datasetId} />}
        {activeTab === 'analysis' && <Analysis datasetId={datasetId} />}
        {activeTab === 'heatmap' && <Heatmap datasetId={datasetId} />}
      </div>
    </div>
  );
};

export default DatasetDetail;