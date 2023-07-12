import { redirect, type V2_MetaFunction } from "@remix-run/node";

export const loader = async () => {
  return redirect(`/stats/berlin`);
};

export const meta: V2_MetaFunction = () => {
  return [
    { title: "Flight CO2 Tracker" },
    {
      name: "description",
      content: "Interesting data about CO2 emissions caused by flights!",
    },
  ];
};

export default function Index() {
  return (
    <div className="flex h-screen justify-center bg-blue-200">
      <div className="flex w-3/4 py-4">
        <h1 className="text-3xl text-white dark:text-black">
          Redirecting to "/stats"...
        </h1>
      </div>
    </div>
  );
}
