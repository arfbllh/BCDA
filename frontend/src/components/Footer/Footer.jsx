import React from "react";
import logo from "../../assets/images/brand/logo.png";
import { BsEnvelope } from "react-icons/bs";
import { FaLocationDot } from "react-icons/fa6";
import { AiOutlineCopyrightCircle, AiOutlineMobile } from "react-icons/ai";
import Image from "../UI/Image";
import { Link } from "react-router-dom";
import { footerServices } from "../../constants/common";
import { HashLink } from "react-router-hash-link";

const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <section className="relative bg-footer__background bg-cover bg-center text-brand__white py-5">
      <div className="absolute top-0 left-0 right-0 bottom-0 backdrop-blur-md" style={{ backgroundColor: "#12002E" }}></div>

      <div className="max-w-screen-xl p-content__padding mx-auto relative">
        <div className="hidden md:flex items-center justify-between py-8 lg:rounded-xl">
          <div>
            <HashLink to={"/#"}>
              <Image
                src={logo}
                alt="Insigina__logo"
                className="w-[80px] md:w-[100px] xl:w-[130px]"
              />
            </HashLink>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center md:items-start gap-x-5">
          <div className="flex-1 flex flex-col md:flex-row justify-start items-center gap-x-5">
            <div className="block md:hidden w-fit mx-auto">
              <HashLink to={"/#"}>
                <Image
                  src={logo}
                  alt="Insigina__logo"
                  className="w-[150px] md:w-[180px] xl:w-[200px]"
                />
              </HashLink>
            </div>

            <div className="lg:ml-10 py-5 md:p-0">
              <p className="text-2xl font-brand__font__bold">Useful Links</p>
              {footerServices.map((item, index) => (
                <Link
                  key={index}
                  className="block w-fit py-0.5 hover:underline duration-300 mx-auto md:mx-0"
                  to={item.route}
                >
                  {item.title}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex-1 flex flex-col items-center md:items-start pb-5 md:p-0">
            <p className="text-2xl font-brand__font__bold">Contacts</p>
            <p className="lg:inline-flex lg:items-center gap-x-2 text-center lg:text-left">
              <FaLocationDot className="hidden lg:block" />
              University of Dhaka
            </p>
            <p className="lg:inline-flex lg:items-center gap-x-2 text-center lg:text-left">
              <BsEnvelope className="hidden lg:block" />
              breastcancerhelpcenter@gmail.com
            </p>
            <p className="lg:inline-flex lg:items-center gap-x-2 text-center lg:text-left">
              <AiOutlineMobile className="hidden lg:block" />
              +880 1890000000
            </p>
          </div>
        </div>

        <div className="border-b w-full mx-auto my-5"></div>
        <div className="flex flex-col md:flex-row justify-between">
          <p className="uppercase flex items-center gap-x-2">
            <AiOutlineCopyrightCircle /> {year} all rights reserved
          </p>
        </div>
      </div>
    </section>
  );
};

export default Footer;
