import React from "react";
import { motion } from "framer-motion"; 

const Featured = () => {
  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-r from-purple-500 to-indigo-600">
      <div className="absolute inset-0 h-full w-full z-0 bg-gradient-to-r from-purple-500 to-indigo-600 opacity-75"></div>

      <div className="relative z-10 flex flex-col justify-center items-center text-center text-white min-h-screen">
        <div className="container mx-auto px-4 py-12">
          <motion.h1
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-4xl md:text-5xl font-bold mb-4"
          >
            Featured Study: Breast Cancer in Bangladeshi Women
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="text-lg md:text-xl mb-8"
          >
            Explore our latest research on the association between hypertension, hyperlipidemia, obesity, and demographic factors with breast cancer in Bangladeshi women. Gain insights into the unique challenges and preventative measures relevant to this population.
          </motion.p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <h2 className="text-xl md:text-2xl font-bold mb-4 text-purple-600">About Breast Cancer</h2>
              <p className="text-gray-800">Understand the disease, its stages, and treatment options.</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <h2 className="text-xl md:text-2xl font-bold mb-4 text-purple-600">Risk Factors</h2>
              <p className="text-gray-800">Learn about various risk factors and how they impact breast cancer development.</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <h2 className="text-xl md:text-2xl font-bold mb-4 text-purple-600">Prevention & Screening</h2>
              <p className="text-gray-800">Find strategies and recommendations for early detection and prevention.</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <h2 className="text-xl md:text-2xl font-bold mb-4 text-purple-600">Research & Studies</h2>
              <p className="text-gray-800">Access the latest research and findings from the scientific community.</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <h2 className="text-xl md:text-2xl font-bold mb-4 text-purple-600">Support & Resources</h2>
              <p className="text-gray-800">Get support through resources for patients, families, and healthcare providers.</p>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Featured;
