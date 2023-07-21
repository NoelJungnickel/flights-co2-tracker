import { useEffect, useState } from "react";
import AirspaceDropdownButton from "./AirspaceDropdownButton";
import LoadingSpinner from "./LoadingSpinner";
import { useNavigation } from "@remix-run/react";

export const airspaceOptions = ["Berlin", "London", "Madrid", "Paris"] as const;

export type AirspaceOption = (typeof airspaceOptions)[number];

type Props = {
  location: AirspaceOption;
  totalCO2LocationKG: number;
  serverstart: number;
};

export const CO2_KG_LAST_VISIT_STORAGE_KEY = "co2_last_visit";

function formatDate(unixTime: number) {
  const milliseconds = unixTime * 1000;
  const date = new Date(milliseconds);

  const day = date.getDate();
  const monthIndex = date.getMonth();
  const year = date.getFullYear();

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const month = monthNames[monthIndex];
  const formattedDate = `${day} ${month} ${year}`;

  return formattedDate;
}

function AirspaceCard({ location, totalCO2LocationKG, serverstart }: Props) {
  const [lastVisitLocationCO2KG, setLastVisitLocationCO2KG] = useState(0);
  const { state: navigationState } = useNavigation();
  const isSubmitting =
    navigationState === "submitting" || navigationState === "loading";

  useEffect(() => {
    const handleTabClosing = () => {
      window.localStorage.setItem(
        `CO2_KG_LAST_VISIT_STORAGE_KEY_${location.toUpperCase()}`,
        totalCO2LocationKG.toString()
      );
    };

    let localCo2LastVisitKG = 0;
    const maybeCO2lastVisitKgString = window.localStorage.getItem(
      `CO2_KG_LAST_VISIT_STORAGE_KEY_${location.toUpperCase()}`
    );

    if (maybeCO2lastVisitKgString !== null) {
      localCo2LastVisitKG = parseFloat(maybeCO2lastVisitKgString);
    }

    setLastVisitLocationCO2KG(localCo2LastVisitKG);

    window.addEventListener("pagehide", handleTabClosing);
    return () => {
      window.removeEventListener("pagehide", handleTabClosing);
    };
  }, [totalCO2LocationKG, location]);

  return (
    <div className="h-fit w-full rounded-lg bg-zinc-700 py-5">
      <div className="flex w-full flex-col items-center justify-center gap-3 px-2 pb-6 sm:flex-row">
        <h1 className="text-center text-2xl font-bold text-sky-50 md:text-3xl">
          Total CO<sub>2</sub> Emissions of Planes in Selected Airspace
        </h1>
        <AirspaceDropdownButton
          options={[...airspaceOptions]}
          defaultOption={location}
          onSelect={(option) => console.log(option)}
          currentLocation={location}
          currentTotalCO2LocationKG={totalCO2LocationKG}
        />
      </div>
      <div className="flex flex-col items-center divide-y divide-zinc-800/30 text-6xl font-bold text-sky-50 sm:flex-row sm:divide-x sm:divide-y-0 md:text-8xl">
        <div className="w-1/2 py-5 text-center">
          {!isSubmitting ? (
            <>
              {Math.floor(totalCO2LocationKG / 1000)}
              <span className="text-xl md:text-5xl">t</span>
            </>
          ) : (
            <div className="flex justify-center py-1.5 sm:py-6">
              <LoadingSpinner />
            </div>
          )}
          <p className="block w-full pt-2 text-base font-normal text-sky-50 sm:hidden">
            CO<sub>2</sub> since serverstart {formatDate(serverstart)}
          </p>
        </div>
        <div className="w-1/2 py-5 text-center">
          {!isSubmitting ? (
            <>
              {(() => {
                const now = Math.floor(totalCO2LocationKG / 1000);
                const lastTime = Math.floor(lastVisitLocationCO2KG / 1000);
                const difference = now - lastTime;

                if (difference < 0) {
                  return 0;
                }

                return difference === now ? 0 : difference;
              })()}
              <span className="text-xl md:text-5xl">t</span>
            </>
          ) : (
            <div className="flex justify-center py-1.5 sm:py-6">
              <LoadingSpinner />
            </div>
          )}
          <p className="block w-full pt-2 text-base font-normal text-sky-50 sm:hidden">
            CO<sub>2</sub> more since your last visit
          </p>
        </div>
      </div>
      <div className="hidden w-full pt-4 text-center sm:flex">
        <p className="w-1/2 text-lg text-sky-50 md:text-xl">
          CO<sub>2</sub> since serverstart {formatDate(serverstart)}
        </p>
        <p className="w-1/2 text-lg text-sky-50 md:text-xl">
          CO<sub>2</sub> more since your last visit
        </p>
      </div>
    </div>
  );
}

export default AirspaceCard;
