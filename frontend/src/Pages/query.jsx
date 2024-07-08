import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Query = () => {
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [geneSymbols, setGeneSymbols] = useState("S100P, PCNA");
  const navigate = useNavigate();

  const datasets = [
    { id: 1, name: "Breast Invasive Carcinoma (TCGA, cell 2015)" },
    { id: 2, name: "Breast Invasive Carcinoma (TCGA, Firehose Legacy)" },
    { id: 3, name: "Breast Invasive Carcinoma (TCGA, Nature 2012)" },
    { id: 4, name: "Breast Invasive Carcinoma (TCGA, PanCancer Atlas)" },
  ];

  const handleDatasetSelect = (dataset) => {
    setSelectedDataset(dataset);
  };

  const handleFormSubmit = (event) => {
    event.preventDefault();
    navigate("/result", { state: { geneSymbols } });
  };

  const handleClearForm = () => {
    setGeneSymbols("");
  };

  return (
    <div className="min-h-screen items-center justify-center">
      <div className="max-w-3xl mx-auto p-8">
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-4 mt-20 text-gray-800">
          Breast Cancer Data Analysis
        </h1>
        <p className="text-lg mb-8 text-gray-700 text-center">
          Please select a dataset from the list on the left and fill out the
          form on the right to query and analyze breast cancer data.
        </p>
      </div>
      <div className="max-w-7xl mx-auto p-8 bg-white rounded-lg shadow-lg grid grid-cols-1 md:grid-cols-5 gap-10">
        <div className="p-6 rounded-lg shadow-md md:col-span-2">
          <h2 className="text-xl font-bold mb-4 ml-6 text-center bg-opacity-50 bg-blue-100 p-2 rounded-lg">
            Dataset
          </h2>

          <ul className="divide-y divide-gray-300">
            {datasets.map((dataset) => (
              <li
                key={dataset.id}
                className={`py-2 cursor-pointer ${
                  selectedDataset === dataset
                    ? "bg-gray-300"
                    : "hover:bg-gray-100"
                }`}
                onClick={() => handleDatasetSelect(dataset)}
              >
                {dataset.name}
              </li>
            ))}
          </ul>
        </div>
        <div
          className="p-10 rounded-lg shadow-md md:col-span-3"
          style={{ backgroundColor: "#DEF9C4" }}
        >
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-2">Scene by gene(s)</h2>
            <div className="border-b-2 border-gray-300 mb-4"></div>
            <h2 className="text-2xl font-semibold mb-4">
              Enter gene symbol(s)
            </h2>
          </div>
          <textarea
            id="geneSymbols"
            name="geneSymbols"
            className="w-full px-3 py-2 border rounded-md text-gray-800"
            rows="4"
            placeholder="Enter gene symbols here"
            value={geneSymbols}
            onChange={(e) => setGeneSymbols(e.target.value)}
          ></textarea>
          <div className="flex justify-center mt-4">
            <button
              type="submit"
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md shadow-md mr-4 transition duration-300"
              onClick={handleFormSubmit}
            >
              Explore
            </button>
            <button
              type="button"
              className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-md shadow-md transition duration-300"
              onClick={handleClearForm}
            >
              Clear Form
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Query;
