type Props = {
  totalCO2BerlinKG: number;
};

function Berlin({ totalCO2BerlinKG }: Props) {
  return (
    <>
      <div className="flex flex-col gap-4">
        <h1 className="self-center text-3xl text-black dark:text-white">
          Total CO2 over Berlin since ...
        </h1>
        <div className="h-32 w-3/4 self-center rounded border-2 md:w-1/2">
          <h1 className="flex h-full items-center justify-center text-3xl text-black dark:text-white">
            {totalCO2BerlinKG} kg
          </h1>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <h1 className="self-center text-3xl text-black dark:text-white">
          Total CO2 since you visited our site
        </h1>
        <div className="h-32 w-3/4 self-center rounded border-2 md:w-1/2">
          <h1 className="flex h-full items-center justify-center text-3xl text-black dark:text-white">
            {totalCO2BerlinKG - totalCO2BerlinKG} kg
          </h1>
        </div>
      </div>
    </>
  );
}

export default Berlin;
