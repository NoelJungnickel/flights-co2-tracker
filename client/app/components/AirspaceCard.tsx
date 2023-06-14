import AirspaceDropdownButton from "./AirspaceDropdownButton";

const airspaceOptions = ["Berlin"] as const;

export type AirspaceOption = (typeof airspaceOptions)[number];

type Props = {
  totalCO2LocationKG: number;
};

function AirspaceCard({ totalCO2LocationKG }: Props) {
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
          {totalCO2LocationKG}
          <span className="text-xl md:text-5xl">kg</span>
          <p className="block w-full pt-2 text-base font-normal text-sky-50 sm:hidden">
            Since 6 June 2023
          </p>
        </div>
        <div className="w-1/2 py-5 text-center">
          10<span className="text-xl md:text-5xl">kg</span>
          <p className="block w-full pt-2 text-base font-normal text-sky-50 sm:hidden">
            Since you opened our site
          </p>
        </div>
      </div>
      <div className="hidden w-full pt-4 text-center sm:flex">
        <p className="w-1/2 text-lg text-sky-50 md:text-xl">
          Since 6 June 2023
        </p>
        <p className="w-1/2 text-lg text-sky-50 md:text-xl">
          Since you opened our site
        </p>
      </div>
    </div>
  );
}

export default AirspaceCard;
