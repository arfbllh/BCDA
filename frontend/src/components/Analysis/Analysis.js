import React, { useState, useEffect, useRef } from "react";
import { datasetService, getErrorMessage } from "../../services/api";
import * as d3 from "d3";
import "./Analysis.css";

const Analysis = ({ datasetId }) => {
  const [analysisType, setAnalysisType] = useState("correlation");
  const [gene, setGene] = useState("");
  const [gene2, setGene2] = useState("");
  const [clinicalFeature, setClinicalFeature] = useState("Age");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);

  // Clinical feature options
  const clinicalFeatureOptions = [
    "Age",
    "Gender",
    "Race",
    "Cancer State",
    "Tumor Histology",
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const params = {
        type: analysisType,
        gene,
        clinicalFeature,
        gene2: gene2
      };

      const data = await datasetService.runAnalysis(datasetId, params);
      if (data && typeof data === "object" && data.error) {
        setError(
          typeof data.error === "string"
            ? data.error
            : data.error?.message || "Analysis request failed"
        );
        setResults(null);
      } else {
        setResults(data);
      }
      setLoading(false);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to run analysis"));
      setLoading(false);
    }
  };

  // Function to create D3 visualizations based on analysis type
  const createVisualization = () => {
    if (!results || !chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    const width = 600;
    const height = 400;
    const margin = { top: 40, right: 30, bottom: 60, left: 60 };

    const svg = d3
      .select(chartRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    switch (analysisType) {
      case "correlation":
        createCorrelationPlot(svg, chartWidth, chartHeight);
        break;
      case "differential":
      case "methylation":
        createBoxSurvival(svg, chartWidth, chartHeight);
        break;
      case "survival":
        createKaplanMeierPlot(svg, chartWidth, chartHeight);
        break;
      default:
        break;
    }
  };

  const createKaplanMeierPlot = (svg, width, height) => {
    // Add title
    if (!results || !results.kmData) {
      console.error("Missing KM data for plot");
      return;
    }

    const kmData = results.kmData;
    const sampleCount = results.sample_count || 0; // Use sample_count from response

    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text(`Kaplan-Meier Survival Plot: ${gene}`);

    // X scale (time)
    const x = d3
      .scaleLinear()
      .domain([0, d3.max(kmData, (d) => d.time) * 1.1]) // Add some padding
      .range([0, width]);

    // Y scale (survival probability)
    const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

    // X axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

    // Y axis
    svg.append("g").call(d3.axisLeft(y));

    // X axis label
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height + 40)
      .attr("text-anchor", "middle")
      .text("Time (months)");

    // Y axis label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .text("Survival Probability");

    // Sort data by time for correct line drawing
    const sortedData = [...kmData].sort((a, b) => a.time - b.time);

    // Line generator for KM plot - using stepBefore for survival curve
    const line = d3
      .line()
      .x((d) => x(d.time))
      .y((d) => y(d.survival))
      .curve(d3.curveStepAfter); // Use proper step curve for KM plots

    // Draw the KM line
    svg
      .append("path")
      .datum(sortedData)
      .attr("fill", "none")
      .attr("stroke", "#4682b4")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add censored points
    svg
      .selectAll(".censored-point")
      .data(kmData.filter((d) => d.censored))
      .enter()
      .append("circle")
      .attr("class", "censored-point")
      .attr("cx", (d) => x(d.time))
      .attr("cy", (d) => y(d.survival))
      .attr("r", 4)
      .style("fill", "white")
      .style("stroke", "red")
      .style("stroke-width", 2);

    // Add uncensored points (events)
    svg
      .selectAll(".uncensored-point")
      .data(kmData.filter((d) => !d.censored))
      .enter()
      .append("circle")
      .attr("class", "uncensored-point")
      .attr("cx", (d) => x(d.time))
      .attr("cy", (d) => y(d.survival))
      .attr("r", 4)
      .style("fill", "red");

    // Add sample count
    svg
      .append("text")
      .attr("x", width - 150)
      .attr("y", 20)
      .style("font-size", "12px")
      .text(`Sample Count: ${sampleCount}`);

    // Add info about censoring in the legend
    svg
      .append("circle")
      .attr("cx", width - 150)
      .attr("cy", 40)
      .attr("r", 4)
      .style("fill", "white")
      .style("stroke", "red")
      .style("stroke-width", 2);

    svg
      .append("text")
      .attr("x", width - 135)
      .attr("y", 42)
      .style("font-size", "12px")
      .text("Censored");

    svg
      .append("circle")
      .attr("cx", width - 150)
      .attr("cy", 60)
      .attr("r", 4)
      .style("fill", "red");

    svg
      .append("text")
      .attr("x", width - 135)
      .attr("y", 62)
      .style("font-size", "12px")
      .text("Event");
  };

  // Correlation analysis scatter plot
  // Updated correlation analysis scatter plot
  const createCorrelationPlot = (svg, width, height) => {
    if (!results || !results.GeneA_point || !results.GeneB_point) {
      console.error("Missing correlation data");
      return;
    }

    // Extract data from the new format
    const geneA = results.GeneA || gene;
    const geneB = results.GeneB || gene2;
    const geneAPoints = results.GeneA_point;
    const geneBPoints = results.GeneB_point;

    // Make sure we have matching arrays
    if (geneAPoints.length !== geneBPoints.length) {
      console.error("Mismatched data points arrays");
      return;
    }

    // Create data points array from the two arrays
    const data_points = geneAPoints.map((x, i) => ({
      geneA_expression: x,
      geneB_expression: geneBPoints[i],
    }));

    // Calculate correlation coefficient
    let sumX = 0,
      sumY = 0,
      sumXY = 0,
      sumX2 = 0,
      sumY2 = 0;
    const n = data_points.length;

    data_points.forEach((point) => {
      const x = point.geneA_expression;
      const y = point.geneB_expression;

      sumX += x;
      sumY += y;
      sumXY += x * y;
      sumX2 += x * x;
      sumY2 += y * y;
    });

    const correlation =
      (n * sumXY - sumX * sumY) /
      (Math.sqrt(n * sumX2 - sumX * sumX) * Math.sqrt(n * sumY2 - sumY * sumY));

    // Add title
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text(`Correlation: ${geneA} vs ${geneB}`);

    // Find the min and max values for scales
    const xExtent = d3.extent(data_points, (d) => d.geneA_expression);
    const yExtent = d3.extent(data_points, (d) => d.geneB_expression);

    // X Scale (gene A expression)
    const x = d3
      .scaleLinear()
      .domain([xExtent[0] * 0.9, xExtent[1] * 1.1])
      .range([0, width]);

    // Y Scale (gene B expression)
    const y = d3
      .scaleLinear()
      .domain([yExtent[0] * 0.9, yExtent[1] * 1.1])
      .range([height, 0]);

    // X Axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

    // X Axis Label
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height + 40)
      .style("text-anchor", "middle")
      .text(`${geneA} Expression`);

    // Y Axis
    svg.append("g").call(d3.axisLeft(y));

    // Y Axis Label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .style("text-anchor", "middle")
      .text(`${geneB} Expression`);

    // Add scatter points
    svg
      .selectAll("circle")
      .data(data_points)
      .enter()
      .append("circle")
      .attr("cx", (d) => x(d.geneA_expression))
      .attr("cy", (d) => y(d.geneB_expression))
      .attr("r", 5)
      .style("fill", "#4682b4")
      .style("opacity", 0.7);

    // Add regression line if correlation exists
    if (data_points.length > 2) {
      // Calculate means
      const xMean = sumX / n;
      const yMean = sumY / n;

      // Calculate slope and intercept for regression line
      const slope =
        correlation *
        (Math.sqrt(sumY2 / n - yMean * yMean) /
          Math.sqrt(sumX2 / n - xMean * xMean));
      const intercept = yMean - slope * xMean;

      const lineData = [
        { x: xExtent[0], y: slope * xExtent[0] + intercept },
        { x: xExtent[1], y: slope * xExtent[1] + intercept },
      ];

      // Add the line
      svg
        .append("path")
        .datum(lineData)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 2)
        .attr(
          "d",
          d3
            .line()
            .x((d) => x(d.x))
            .y((d) => y(d.y))
        );
    }

    // Calculate a simple estimate of p-value based on correlation and sample size
    // This is an approximation, not exact statistical test
    const t =
      correlation * Math.sqrt((n - 2) / (1 - correlation * correlation));
    const pValue = 2 * (1 - cumulativeDistribution(Math.abs(t), n - 2));

    // Add statistics
    svg
      .append("text")
      .attr("x", width - 150)
      .attr("y", 20)
      .text(`r = ${correlation.toFixed(3)}`)
      .style("font-size", "12px");

    svg
      .append("text")
      .attr("x", width - 150)
      .attr("y", 40)
      .text(`p-value ≈ ${pValue.toFixed(4)}`)
      .style("font-size", "12px");

    svg
      .append("text")
      .attr("x", width - 150)
      .attr("y", 60)
      .text(`n = ${n} data points`)
      .style("font-size", "12px");
  };

  // Helper function to approximate the cumulative t-distribution
  function cumulativeDistribution(t, df) {
    // This is a simplified approximation
    const x = df / (df + t * t);
    let result = 1 - 0.5 * Math.pow(x, df / 2);
    return result;
  }


  /**
   * Convert pandas describe / groupby.describe JSON into per-group box stats.
   * Supports metric-keyed or group-keyed shapes from Flask/jsonify.
   */
  const describeStatsToBoxData = (stats) => {
    if (!stats || typeof stats !== "object") return {};

    const boxFromRow = (row) => {
      const lo = row.min;
      const a = row["25%"] ?? row["25% "];
      const b = row["50%"] ?? row["50% "];
      const c = row["75%"] ?? row["75% "];
      const hi = row.max;
      if (
        [lo, a, b, c, hi].every(
          (v) => typeof v === "number" && !Number.isNaN(v)
        )
      ) {
        return { min: lo, Q1: a, median: b, Q3: c, max: hi };
      }
      return null;
    };

    const byGroup = {};
    let groupKeyed = false;
    for (const [key, row] of Object.entries(stats)) {
      if (typeof row !== "object" || row === null) continue;
      if (
        ("50%" in row || "50% " in row) &&
        ("25%" in row || "25% " in row)
      ) {
        const b = boxFromRow(row);
        if (b) {
          byGroup[String(key)] = b;
          groupKeyed = true;
        }
      }
    }
    if (groupKeyed) return byGroup;

    const q1 = stats["25%"] || stats["25% "];
    const q2 = stats["50%"] || stats["50% "];
    const q3 = stats["75%"] || stats["75% "];
    const mins = stats.min;
    const maxs = stats.max;
    if (!q1 || !q2 || !q3 || typeof q1 !== "object") return {};
    const groups = Object.keys(q1);
    const out = {};
    for (const g of groups) {
      const row = {
        min: mins ? mins[g] : undefined,
        "25%": q1[g],
        "50%": q2[g],
        "75%": q3[g],
        max: maxs ? maxs[g] : undefined,
      };
      const b = boxFromRow(row);
      if (b) out[String(g)] = b;
    }
    return out;
  };

  const createBoxSurvival = (svg, width, height) => {
    if (!results || !results.analyses || !results.analyses[clinicalFeature]) {
      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .style("font-size", "13px")
        .text("No data for the selected clinical feature.");
      return;
    }

    const survivalData = results.analyses[clinicalFeature];
    const pValue = survivalData.p_value ?? 0;
    let boxData = {};

    if (survivalData.plots && typeof survivalData.plots === "object") {
      boxData = { ...survivalData.plots };
    } else if (survivalData.stats) {
      boxData = describeStatsToBoxData(survivalData.stats);
    }

    if (Object.keys(boxData).length === 0) {
      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .text(
          "Chart not available for this response (see numeric summaries below)."
        );
      return;
    }

    const plotLabel =
      analysisType === "differential"
        ? "Differential (methylation pipeline)"
        : "Methylation";

    const isCategorical = [
      "Gender",
      "Race",
      "Cancer State",
      "Tumor Histology",
      "Age",
    ].includes(clinicalFeature);

    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", -20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text(`${plotLabel}: ${gene} by ${clinicalFeature}`);

    const x = d3
      .scaleBand()
      .domain(Object.keys(boxData))
      .range([0, width])
      .padding(isCategorical ? 0.4 : 0.3);

    // Collect all values to determine y-scale
    const allValues = [];
    Object.values(boxData).forEach((group) => {
      [group.min, group.Q1, group.median, group.Q3, group.max].forEach(
        (val) => {
          if (typeof val === "number" && !isNaN(val)) {
            allValues.push(val);
          }
        }
      );
    });

    // Y scale for survival values
    const yMin = Math.min(...allValues) * 0.9 || 0;
    const yMax = Math.max(...allValues) * 1.1 || 100;

    const y = d3.scaleLinear().domain([yMin, yMax]).range([height, 0]).nice();

    // X axis with proper rotation for categorical data
    const xAxis = svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x));

    // Rotate labels if categorical and there are many categories
    if (isCategorical && Object.keys(boxData).length > 3) {
      xAxis
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em");
    }

    // Y axis
    svg.append("g").call(d3.axisLeft(y));

    // X axis label - more specific for categorical data
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height + (isCategorical ? 45 : 40)) // More space for rotated labels
      .attr("text-anchor", "middle")
      .text(
        isCategorical ? clinicalFeature + " Categories" : "Expression Groups"
      );

    // Y axis label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .text("Distribution (values per group)");

    // Color scale for categorical data
    const colorScale = isCategorical
      ? d3.scaleOrdinal(d3.schemeCategory10)
      : d3
          .scaleOrdinal()
          .domain(Object.keys(boxData))
          .range(["#4dabf7", "#ff6b6b"].slice(0, Object.keys(boxData).length));

    // Draw each box plot
    Object.entries(boxData).forEach(([group, data]) => {
      const boxWidth = x.bandwidth();
      const groupX = x(group);

      // Determine color based on data type
      const fillColor = isCategorical
        ? colorScale(group)
        : group.toLowerCase().includes("high")
        ? "#ff6b6b"
        : "#4dabf7";

      // Box (IQR)
      svg
        .append("rect")
        .attr("x", groupX)
        .attr("y", y(data.Q3))
        .attr("width", boxWidth)
        .attr("height", Math.max(0, y(data.Q1) - y(data.Q3)))
        .attr("fill", fillColor)
        .attr("stroke", "black")
        .attr("opacity", 0.8); // Slightly transparent for better visualization

      // Median line
      svg
        .append("line")
        .attr("x1", groupX)
        .attr("x2", groupX + boxWidth)
        .attr("y1", y(data.median))
        .attr("y2", y(data.median))
        .attr("stroke", "black")
        .attr("stroke-width", 2);

      // Min whisker
      svg
        .append("line")
        .attr("x1", groupX + boxWidth / 2)
        .attr("x2", groupX + boxWidth / 2)
        .attr("y1", y(data.Q1))
        .attr("y2", y(data.min))
        .attr("stroke", "black");

      // Max whisker
      svg
        .append("line")
        .attr("x1", groupX + boxWidth / 2)
        .attr("x2", groupX + boxWidth / 2)
        .attr("y1", y(data.Q3))
        .attr("y2", y(data.max))
        .attr("stroke", "black");

      // Min whisker cap
      svg
        .append("line")
        .attr("x1", groupX + boxWidth / 4)
        .attr("x2", groupX + (boxWidth * 3) / 4)
        .attr("y1", y(data.min))
        .attr("y2", y(data.min))
        .attr("stroke", "black");

      // Max whisker cap
      svg
        .append("line")
        .attr("x1", groupX + boxWidth / 4)
        .attr("x2", groupX + (boxWidth * 3) / 4)
        .attr("y1", y(data.max))
        .attr("y2", y(data.max))
        .attr("stroke", "black");

      // Improve label positioning
      if (!isCategorical || Object.keys(boxData).length <= 3) {
        // Simple labels for non-categorical or few categories
        svg
          .append("text")
          .attr("x", groupX + boxWidth / 2)
          .attr("y", height + 15)
          .attr("text-anchor", "middle")
          .style("font-size", "12px")
          .text(group);
      }
    });

    // Add p-value
    svg
      .append("text")
      .attr("x", width - 200)
      .attr("y", 20)
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .text(`p-value: ${pValue.toFixed(4)}`);

    // Add dynamic legend based on data type
    const legendY = 40;
    const legendItems = isCategorical
      ? Object.keys(boxData).map((category) => ({
          text: category,
          color: colorScale(category),
        }))
      : [
          { text: "High Expression", color: "#ff6b6b" },
          { text: "Low Expression", color: "#4dabf7" },
        ];

    // Create legend
    legendItems.forEach((item, i) => {
      // Rectangle
      svg
        .append("rect")
        .attr("x", width - 150)
        .attr("y", legendY + i * 25)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill", item.color);

      // Text
      svg
        .append("text")
        .attr("x", width - 130)
        .attr("y", legendY + i * 25 + 8)
        .style("font-size", "12px")
        .attr("alignment-baseline", "middle")
        .text(item.text);
    });
  };

  // Call createVisualization whenever results change
  useEffect(() => {
    if (results) {
      createVisualization();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- D3 chart sync; functions close over latest state
  }, [results, analysisType, clinicalFeature, gene, gene2]);

  return (
    <div className="analysis-container">
      <h2>Run Analysis</h2>

      <form onSubmit={handleSubmit} className="analysis-form">
        <div className="form-group">
          <label htmlFor="analysisType">Analysis Type:</label>
          <select
            id="analysisType"
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
            required
          >
            <option value="correlation">Correlation Analysis</option>
            <option value="differential">Differential Expression</option>
            <option value="survival">Survival Analysis</option>
            <option value="methylation">Methylation Analysis</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="gene">Gene:</label>
          <input
            type="text"
            id="gene"
            value={gene}
            onChange={(e) => setGene(e.target.value)}
            placeholder="e.g., TP53"
            required
          />
        </div>
        {analysisType === "correlation" && (
          <div className="form-group">
            <label htmlFor="gene">Gene 2:</label>
            <input
              type="text"
              id="gene2"
              value={gene2}
              onChange={(e) => setGene2(e.target.value)}
              placeholder="e.g., TP53"
              required
            />
          </div>
        )}

        {analysisType !== "correlation" && analysisType !== "survival" && (
          <div className="form-group">
            <label htmlFor="clinicalFeature">Clinical Feature:</label>
            <select
              id="clinicalFeature"
              value={clinicalFeature}
              onChange={(e) => setClinicalFeature(e.target.value)}
              required
            >
              {clinicalFeatureOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? "Running..." : "Run Analysis"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {results && (
        <div className="analysis-results">
          <h3>Analysis Results</h3>
          <div className="results-container">
            {results.analyses &&
              Object.entries(results.analyses)
                .filter(
                  ([key, value]) =>
                    typeof value !== "object" || key === "Methylations"
                )
                .map(([key, value]) => (
                  <div key={key} className="result-item">
                    <strong>{key.replace("_", " ")}:</strong>{" "}
                    {typeof value === "object"
                      ? "Available"
                      : Array.isArray(value)
                      ? value.join(", ")
                      : value}
                  </div>
                ))}
          </div>

          {/* D3.js visualization container */}
          <div className="result-visualization" ref={chartRef}></div>
        </div>
      )}
    </div>
  );
};

export default Analysis;
