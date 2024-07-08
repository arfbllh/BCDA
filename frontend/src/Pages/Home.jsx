import { lazy, Suspense, useEffect, useState } from "react";
import Spinner from "../components/common/Spinner";
import Banner from "../components/home/banner";
import Featured from "../components/home/featured";

const Home = () => {



  return (
    <div>
       <Suspense
        fallback={
          <Spinner className="h-screen flex flex-col justify-center items-center" />
        }
      >
        <Banner />
      </Suspense>

      <Suspense
        fallback={
          <Spinner className="h-screen flex flex-col justify-center items-center" />
        }
      >
        <Featured />
      </Suspense>
      

    </div>
  );
};

export default Home;