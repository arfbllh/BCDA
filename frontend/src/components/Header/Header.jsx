import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { IoIosArrowDown } from "react-icons/io";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import Logo from "./Logo";
import PcNavigation from "./PcNavigation";
import clientProfile from "../../assets/images/profile/user.png";
import spProfile from "../../assets/images/profile/profile.png";
import { BASE_URL } from "../../utils/config";

const Header = () => {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  return (
    <header
      className={`w-full h-20 md:h-24 flex justify-between items-center duration-300 font-brand__font_family__regular ${
        isHomePage
          ? "bg-transparent absolute top-0 left-0 right-0 lg:h-28"
          : "bg-white lg:h-24 shadow sticky top-0 z-50"
      }`}
    >
      <div className="max-w-screen-xl mx-auto w-full z-50 text-brand__white p-content__padding">
        <div className="flex justify-between items-center">
          <Logo />
          <PcNavigation />
         
        </div>
      </div>
    </header>
  );
};

export default Header;
