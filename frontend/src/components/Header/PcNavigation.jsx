import React, { useState } from "react";
import { HashLink } from "react-router-hash-link";
import { useLocation } from "react-router-dom";
import { navItems } from "../../constants/navigation";
import Cookies from "js-cookie";
import { MdWork } from "react-icons/md";

const PcNavigation = () => {
  const location = useLocation();
  const [activeLink, setActiveLink] = useState(""); 

  const isHomePage = location.pathname === "/";

  const handleLinkClick = (title) => {
    setActiveLink(title); 
  };

  return (
    <div
      className={`hidden lg:block backdrop-filter backdrop-blur-lg font-brand__font__semibold ${
        isHomePage
          ? "text-white border-brand__gray__border"
          : "text-primary border-primary"
      }`}
    >
      <div className="flex items-center px-1 py-0.5 duration-300">
        {navItems.map(({ title, route, Icon }) => (
          <li
            className={`group flex items-center rounded-full duration-300 relative ${
              activeLink === title
                ? "bg-primary text-white"
                : isHomePage
                ? "hover:bg-bg__gray"
                : "hover:bg-primary hover:text-white"
            }`}
            key={title}
          >
            <HashLink
              className={`rounded-full mx-1 capitalize py-3 xl:py-3 px-4 text-black__font__size__sm flex items-center hover:bg-primary hover:text-white ${
                activeLink === title ? "text-white" : ""
              }`}
              to={route}
              style={{ textDecoration: "none" }}
              onClick={() => handleLinkClick(title)}
            >
              {Icon && <Icon className="mr-2" />}
              {title}
            </HashLink>
          </li>
        ))}
      </div>
    </div>
  );
};

export default PcNavigation;
