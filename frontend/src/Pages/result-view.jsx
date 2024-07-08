import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ResultView = () => {
  const location = useLocation();
  const { gene, link } = location.state;
  const [selectedCancer, setSelectedCancer] = useState(null);
  const [selectedSampleType, setSelectedSampleType] = useState("");

  const cancers = [
    { id: 1, name: "ER" },
    { id: 2, name: "PR" },
    { id: 3, name: "HER2" },
    { id: 4, name: "TNBC" },
  ];

  const sampleTypes = [
    "Cancer Stage",
    "Race",
    "Gender",
    "Age",
    "Major Subclass",
    "Major Subclass with TNBC",
    "Menopause Status",
    "Nodal Metastasis status"
  ];

  const handleCancerSelect = (cancer) => {
    setSelectedCancer(cancer);
  };

  const handleSampleTypeSelect = (event) => {
    setSelectedSampleType(event.target.value);
  };

  const sampleData = {
    labels: [
      'Normal (n=114)',
      '21-40 yrs (n=97)',
      '41-60 yrs (n=150)',
      '61-80 yrs (n=90)',
      '81+ yrs (n=25)'
    ],
    datasets: [
      {
        label: selectedSampleType || "Sample Type",
        data: [1200, 1500, 800, 600, 900],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Breast Invasive Carcinoma',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'TCGA Samples',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Transaction per Million',
        },
      },
    },
  };

  return (
    <div className="min-h-screen items-center justify-center mt-2">
      <div className="max-w-7xl mx-auto p-8 bg-white rounded-lg shadow-lg grid grid-cols-1 md:grid-cols-6 gap-10">
        <div className="p-6 rounded-lg shadow-md md:col-span-2">
          <h2 className="text-xl font-bold mb-4 ml-6 text-center bg-opacity-50 bg-blue-100 p-2 rounded-lg">
            Select Cancer
          </h2>

          <ul className="divide-y divide-gray-300">
            {cancers.map((cancer) => (
              <li
                key={cancer.id}
                className={`py-2 cursor-pointer ${
                  selectedCancer === cancer
                    ? "bg-gray-300"
                    : "hover:bg-gray-100"
                }`}
                onClick={() => handleCancerSelect(cancer)}
              >
                {cancer.name}
              </li>
            ))}
          </ul>
        </div>
        <div
          className="p-10 rounded-lg shadow-md md:col-span-4"
          style={{ backgroundColor: "#DEF9C4" }}
        >
          <div className="text-center flex mb-4">
            <h2 className="text-2xl font-semibold mb-2">
              {gene} {link} based on
            </h2>
            <select
              id="sample-type"
              value={selectedSampleType}
              onChange={handleSampleTypeSelect}
              className="block p-2 border bg-blue-100 rounded-md ml-4"
            >
              <option value="" disabled>Select sample type</option>
              {sampleTypes.map((type, index) => (
                <option key={index} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <div className="border-b-2 border-gray-300 mb-4"></div>

          <div className="bg-white p-4 rounded-lg shadow-lg">
            <Bar data={sampleData} options={options} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultView;
