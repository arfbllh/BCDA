// src/components/DatasetDetail/DatasetDetail.js
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useParams, useNavigate, useSearchParams } from 'react-router-dom';
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

const VALID_TAB_IDS = new Set(TABS.map((t) => t.id));

const DatasetDetail = () => {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataStatus, setDataStatus] = useState(null);

  const activeTab = useMemo(() => {
    const raw = searchParams.get('tab');
    if (raw && VALID_TAB_IDS.has(raw)) {
      return raw;
    }
    return 'summary';
  }, [searchParams]);

  const setActiveTab = useCallback(
    (id) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (id === 'summary') {
            next.delete('tab');
          } else {
            next.set('tab', id);
          }
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      setDataset(null);
      setDataStatus(null);
      try {
        const meta = await datasetService.getDatasetMeta(datasetId);
        if (cancelled) return;
        if (!meta) {
          setError(null);
          setDataset(null);
        } else {
          setDataset(meta);
          try {
            const st = await datasetService.getStudyDataStatus(datasetId);
            if (!cancelled) {
              setDataStatus(st);
            }
          } catch {
            if (!cancelled) {
              setDataStatus(null);
            }
          }
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
      {dataStatus &&
        (!dataStatus.clinical_patient_ingested ||
          !dataStatus.expression_matrix_file_present) && (
        <Alert variant="info" className="mb-3" role="status">
          <Alert.Heading className="h6">Data plane status</Alert.Heading>
          <ul className="mb-0 small">
            <li>
              Clinical table ingested:{' '}
              <strong>{dataStatus.clinical_patient_ingested ? 'yes' : 'no'}</strong>
              {!dataStatus.clinical_patient_ingested &&
                ' — run ingestion after placing cBioPortal-style files under DATASETS_BASE_DIR.'}
            </li>
            <li>
              Expression matrix CSV on disk:{' '}
              <strong>{dataStatus.expression_matrix_file_present ? 'yes' : 'no'}</strong>
            </li>
          </ul>
        </Alert>
      )}

      <p className="dataset-jobs-link mb-3">
        <button
          type="button"
          className="btn btn-link p-0 align-baseline"
          onClick={() =>
            navigate(`/jobs?study=${encodeURIComponent(dataset.id)}`)
          }
        >
          Async jobs for this study
        </button>
      </p>

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
