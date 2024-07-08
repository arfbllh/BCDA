import React from "react";
import bg from "../../assets/images/banner/bg.jpg";
import women from "../../assets/images/banner/women.png";

const Banner = () => {
  return (
    <div
      className="min-h-screen flex flex-col justify-center py-20 bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="container mx-auto px-4">
        <div className="flex flex-wrap items-center">
          <div className="w-full md:w-1/2 text-left">
            <h1 className="text-5xl font-bold mb-6 text-pink-600  bg-opacity-75 ">
              Welcome to Breast Cancer Analysis
            </h1>

            <p className="text-xl mb-6 text-gray-800">
              Your trusted source for comprehensive information and research on
              breast cancer.
            </p>
            <p className="text-lg mb-6 text-gray-700">
              At Breast Cancer Analysis, we are dedicated to empowering
              individuals, healthcare professionals, and researchers with the
              knowledge and resources needed to understand, prevent, and treat
              breast cancer. Explore our site to discover in-depth articles, the
              latest research, and practical tips on managing risk factors and
              improving breast health.
            </p>
            <div className="flex space-x-4">
              <a
                href="/about-breast-cancer"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg"
              >
                Learn More
              </a>
              <a
                href="/contact-us"
                className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg"
              >
                Contact Us
              </a>
            </div>
          </div>
          <div className="w-full md:w-1/2 flex justify-center mt-10 md:mt-0">
            <img
               src={women} 
              alt="Breast Cancer Awareness"
              className="max-w-full h-auto"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Banner;
