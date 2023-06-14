import { useEffect, useState } from "react";
import AirspaceDropdownButton from "./AirspaceDropdownButton";

const airspaceOptions = ["Berlin"] as const;

export type AirspaceOption = (typeof airspaceOptions)[number];

type Props = {
  totalCO2LocationKG: number;
};

export const CO2_KG_LAST_VISIT_STORAGE_KEY = "co2_last_visit";

function AirspaceCard({ totalCO2LocationKG }: Props) {
  const [lastVisitLocationCO2KG, setLastVisitLocationCO2KG] = useState(0);

  const handleTabClosing = () => {
    window.localStorage.setItem(
      CO2_KG_LAST_VISIT_STORAGE_KEY,
      totalCO2LocationKG.toString()
    );
  };

  useEffect(() => {
    let localCo2LastVisitKG = 0;
    const maybeCO2lastVisitKgString = window.localStorage.getItem(
      CO2_KG_LAST_VISIT_STORAGE_KEY
    );

    if (maybeCO2lastVisitKgString !== null) {
      localCo2LastVisitKG = parseFloat(maybeCO2lastVisitKgString);
    }

    setLastVisitLocationCO2KG(localCo2LastVisitKG);

    window.addEventListener("unload", handleTabClosing);
    return () => {
      window.removeEventListener("unload", handleTabClosing);
    };
  }, []);

  return (
    <div className="h-fit w-full rounded-lg bg-zinc-700 py-5">
      <div className="flex w-full justify-center gap-3 pb-6">
        <h1 className="text-center text-3xl font-bold text-sky-50">
          Airspace Stats
        </h1>
        <AirspaceDropdownButton
          options={[...airspaceOptions]}
          defaultOption="Berlin"
          onSelect={(option) => console.log(option)}
        />
      </div>
      <div className="flex flex-col items-center divide-y divide-zinc-800/30 text-6xl font-bold text-sky-50 sm:flex-row sm:divide-x sm:divide-y-0 md:text-8xl">
        <div className="w-1/2 py-5 text-center">
          {Math.floor(totalCO2LocationKG / 1000)}
          <span className="text-xl md:text-5xl">t</span>
          <p className="block w-full pt-2 text-base font-normal text-sky-50 sm:hidden">
            since 10 June 2023
          </p>
        </div>
        <div className="w-1/2 py-5 text-center">
          {(() => {
            const now = Math.floor(totalCO2LocationKG / 1000);
            const lastTime = Math.floor(lastVisitLocationCO2KG / 1000);
            const difference = now - lastTime;
            return difference <= now ? 0 : difference;
          })()}
          <span className="text-xl md:text-5xl">t</span>
          <p className="block w-full pt-2 text-base font-normal text-sky-50 sm:hidden">
            more since your last visit
          </p>
        </div>
      </div>
      <div className="hidden w-full pt-4 text-center sm:flex">
        <p className="w-1/2 text-lg text-sky-50 md:text-xl">
          since 10 June 2023
        </p>
        <p className="w-1/2 text-lg text-sky-50 md:text-xl">
          more since your last visit
        </p>
      </div>
    </div>
  );
}

export default AirspaceCard;
