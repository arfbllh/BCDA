import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

const Result = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const geneSymbols = location.state?.geneSymbols || "";

  const genesList = ["S100P", "PCNA", "ERBB2"];
  const genes = geneSymbols.split(",").map((gene) => gene.trim());

  const links = ["Expression", "Correlation", "Methylation", "Survival"];

  const handleLinkClick = (gene, link) => {
    navigate("/result-view", { state: { gene, link } });
  };

  return (
    <div className="min-h-screen flex py-4 justify-center">
      <div className="max-w-7xl mx-auto p-8 bg-white rounded-lg shadow-lg px-20">
        <h2 className="text-2xl font-semibold mb-4 text-center bg-gradient-to-r from-purple-100 to-indigo-200 text-blue-800 rounded-md px-4 py-2">
          Gene(s) and Links for Analysis
        </h2>
        <div className="border-b-2 border-gray-300 mb-4"></div>
        <div className="grid grid-cols-1 gap-8 justify-center">
          <div className="w-full">
            <table className="min-w-full leading-normal mx-auto">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-center text-lg font-semibold bg-gradient-to-r from-purple-100 to-indigo-200 text-blue-800 rounded-md">Input Genes</th>
                  <th className="px-4 py-2 text-center text-lg font-semibold bg-gradient-to-r from-purple-100 to-indigo-200 text-blue-800 rounded-md">Links for Analysis</th>
                </tr>
              </thead>
              <tbody>
                {genes.map((gene, index) => (
                  <tr key={index}>
                    <td className="border-b border-gray-200 px-4 py-4 text-center">
                      {genesList.includes(gene) ? (
                        <h3 className="text-xl font-semibold">{gene}</h3>
                      ) : (
                        <span className="text-red-500">doesn't exist</span>
                      )}
                    </td>
                    <td className="border-b border-gray-200 px-4 py-4 text-center">
                      {genesList.includes(gene) && (
                        <div className="flex justify-center">
                          {links.map((link, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleLinkClick(gene, link)}
                              className="text-blue-600 hover:text-blue-800 mx-2 bg-gradient-to-r from-pink-100 to-red-200 text-blue-800 rounded-md px-4 py-2"
                            >
                              {link}
                            </button>
                          ))}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Result;
