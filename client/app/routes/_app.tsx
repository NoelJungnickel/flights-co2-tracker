import { Outlet, type V2_MetaFunction } from "@remix-run/react";
import Header from "~/components/Header";

export const meta: V2_MetaFunction = () => {
  return [
    { title: "Flights CO2 Tracker" },
    {
      name: "description",
      content: "Interesting data about CO2 emissions caused by flights!",
    },
  ];
};

function Stats() {
  return (
    <>
      <Header />
      <div className="flex max-h-fit min-h-screen justify-center bg-zinc-800 font-poppins">
        <div className="flex w-full justify-center py-4">
          <Outlet />
        </div>
      </div>
    </>
  );
}

export default Stats;
