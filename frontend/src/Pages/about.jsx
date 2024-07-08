import React from "react";
import { motion } from "framer-motion"; 

const About = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-blue-200 px-20">
      <div className="w-full mx-4 md:max-w-7xl mx-4 md:mx-auto md:mx-auto p-8">
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-center mb-8 text-gray-800">About Our Breast Cancer Analysis</h1>
          <p className="text-lg mb-8 text-gray-700">
            Welcome to our breast cancer analysis website! We are dedicated to advancing the understanding of breast cancer among Bangladeshi women. Through rigorous research and studies, we investigate the intricate relationship between hypertension, hyperlipidemia, obesity, demographic factors, and breast cancer risk.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4 text-purple-600">Our Mission</h2>
              <p className="text-gray-800">
                Our mission is to empower individuals and healthcare providers with knowledge and resources to prevent, diagnose, and treat breast cancer effectively in Bangladeshi women.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4 text-purple-600">Our Vision</h2>
              <p className="text-gray-800">
                We envision a future where breast cancer incidence and mortality rates in Bangladesh are significantly reduced through education, awareness, and accessible healthcare solutions.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4 text-purple-600">Key Objectives</h2>
              <ul className="list-disc list-inside text-gray-800">
                <li>Conduct comprehensive research studies on breast cancer risk factors.</li>
                <li>Promote early detection and screening programs.</li>
                <li>Provide educational resources for patients and healthcare professionals.</li>
                <li>Advocate for policies that improve breast cancer care and support.</li>
              </ul>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4 text-purple-600">Our Team</h2>
              <p className="text-gray-800">
                Meet our dedicated team of researchers, healthcare professionals, and advocates committed to combating breast cancer in Bangladesh.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default About;
