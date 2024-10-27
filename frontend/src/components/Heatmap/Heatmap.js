// src/components/Heatmap/Heatmap.js
import React, { useState, useEffect, useCallback } from "react";
import { Alert, Spinner } from "react-bootstrap";
import "./Heatmap.css";
import Plotly from "plotly.js-dist";
import { datasetService, getErrorMessage } from "../../services/api";

const Heatmap = ({ datasetId }) => {
  const studyLabel = datasetId || "study";
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plotData, setPlotData] = useState(null);

  const fetchHeatmapData = useCallback(async () => {
    if (!datasetId) {
      setLoading(false);
      setError("No study selected.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const plot = await datasetService.getHeatmapPlotly(datasetId);
      setPlotData(plot);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load heatmap"));
    } finally {
      setLoading(false);
    }
  }, [datasetId]);

  useEffect(() => {
    setPlotData(null);
    fetchHeatmapData();
  }, [datasetId, fetchHeatmapData]);

  useEffect(() => {
    if (plotData && !loading) {
      const plotElement = document.getElementById("heatmap-plot");

      if (plotElement) {
        Plotly.newPlot(plotElement, plotData.data, plotData.layout, {
          responsive: true,
          toImageButtonOptions: {
            format: "png",
            filename: `heatmap_${studyLabel}`,
            height: 800,
            width: 1200,
            scale: 1,
          },
        });

        return () => {
          Plotly.purge(plotElement);
        };
      }
    }
  }, [plotData, loading, studyLabel]);

  return (
    <div className="heatmap-container">
      <h2>Gene Expression Heatmap</h2>

      <div className="heatmap-disclaimer" role="note">
        <strong>Note:</strong> The heatmap reads{" "}
        <code>data_mrna_seq_v2_rsem_zscores_ref_all_samples.csv</code> for study{" "}
        <code>{studyLabel}</code> under <code>DATASETS_BASE_DIR</code> on the API host (first 200×200
        genes/samples). Ingest large matrices to Parquet separately; this view is for bundled CSVs.
      </div>

      {loading && (
        <div className="loading-container" aria-busy="true">
          <Spinner animation="border" role="status" />
          <p className="mt-3 text-muted">Loading heatmap…</p>
        </div>
      )}

      {error && (
        <Alert variant="danger" className="mt-2">
          <Alert.Heading className="h5">Could not load heatmap</Alert.Heading>
          <p className="mb-2">{error}</p>
          <button type="button" className="retry-btn" onClick={fetchHeatmapData}>
            Retry
          </button>
        </Alert>
      )}

      <div
        id="heatmap-plot"
        className="heatmap-plot"
        style={{
          display: loading || error ? "none" : "block",
          width: "100%",
          height: "800px",
        }}
      ></div>

      {!loading && !error && (
        <div className="heatmap-controls">
          <button
            className="heatmap-download-btn"
            onClick={() => {
              const plotElement = document.getElementById("heatmap-plot");
              Plotly.downloadImage(plotElement, {
                format: "png",
                filename: `heatmap_${studyLabel}`,
                height: 800,
                width: 1200,
                scale: 2,
              });
            }}
          >
            Download PNG
          </button>
        </div>
      )}
    </div>
  );
};

export default Heatmap;
