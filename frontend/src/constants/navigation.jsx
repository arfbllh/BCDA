import { BiHome } from "react-icons/bi";
import { IoMdContacts } from "react-icons/io";
import { MdQueryStats } from "react-icons/md";
import { FaDatabase } from "react-icons/fa6";
import { FcAbout } from "react-icons/fc";

export const navItems = [
  { title: "home", route: "/", Icon: BiHome },
  { title: "Query", route: "/query", Icon: MdQueryStats }, 
  { title: "Visualize your Data", route: "/", Icon: FaDatabase }, 
  // { title: "about us", route: "/about-us", Icon: GrContactInfo },
  { title: "About", route: "/about", Icon: FcAbout },
];

