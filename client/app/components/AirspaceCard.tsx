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
      <div className="flex divide-x divide-zinc-800/30 text-8xl font-bold text-sky-50">
        <div className="w-1/2 py-5 text-center">
          {totalCO2LocationKG}
          <span className="text-5xl">kg</span>
        </div>
        <div className="w-1/2 py-5 text-center">
          10<span className="text-5xl">kg</span>
        </div>
      </div>
      <div className="flex w-full pt-4 text-center">
        <p className="w-1/2 text-xl text-sky-50">6 June 2023</p>
        <p className="w-1/2 text-xl text-sky-50">Since you opened our site</p>
      </div>
    </div>
  );
}

export default AirspaceCard;
