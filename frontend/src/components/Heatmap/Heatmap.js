// src/components/Heatmap/Heatmap.js
import React, { useState, useEffect } from "react";
import "./Heatmap.css";
import Plotly from "plotly.js-dist";
import { datasetService, getErrorMessage } from "../../services/api";

const Heatmap = ({ datasetId, datasetName = "brca_tcga_pub2015" }) => {
  const studyLabel = datasetId || datasetName;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plotData, setPlotData] = useState(null);

  useEffect(() => {
    fetchHeatmapData();
  }, []);

  const fetchHeatmapData = async () => {
    setLoading(true);
    setError(null);

    try {
      const plot = await datasetService.getHeatmapPlotly();
      setPlotData(plot);
    } catch (err) {
      console.error("Error fetching heatmap data:", err);
      setError(getErrorMessage(err, "Failed to load heatmap"));
    } finally {
      setLoading(false);
    }
  };

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

  const tcgaStudyId = "brca_tcga_pub2015";

  return (
    <div className="heatmap-container">
      <h2>Gene Expression Heatmap</h2>

      <div className="heatmap-disclaimer" role="note">
        <strong>Note:</strong> The API currently serves a fixed expression matrix slice for{" "}
        <code>{tcgaStudyId}</code> (subset of genes and samples). It does not yet accept a study
        parameter; the plot is the same regardless of the study you opened. Filenames use your
        current route: <code>{studyLabel}</code>.
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loader"></div>
          <p>Loading heatmap data...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <h3>Error Loading Heatmap</h3>
          <p>{error}</p>
          <button className="retry-btn" onClick={fetchHeatmapData}>
            Retry
          </button>
        </div>
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
            className="download-btn"
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
