import type { TypedResponse } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  isRouteErrorResponse,
  useLoaderData,
  useRouteError,
} from "@remix-run/react";
import AirspaceCard from "~/components/AirspaceCard";
import type { LeaderboardEntry } from "~/components/LeaderboardCard";
import LeaderboardCard from "~/components/LeaderboardCard";

type Stats = {
  totalLocationCO2KG: number;
  leaderboardContent: LeaderboardEntry[];
};

export async function loader(): Promise<TypedResponse<Stats>> {
  let API_URL = "http://35.210.64.77:8000/api/total/berlin";
  // if (process.env.NODE_ENV === "development") {
  //   API_URL = "http://127.0.0.1:8000/api/total/berlin";
  // }

  const totalBerlinCO2KgReponse = await fetch(API_URL);

  if (!totalBerlinCO2KgReponse) {
    throw new Response("Internal Server Error", {
      status: 500,
    });
  }

  const totalBerlinCO2Kg = await totalBerlinCO2KgReponse.json();

  return json({
    totalLocationCO2KG: totalBerlinCO2Kg,
    leaderboardContent: [
      { placing: 1, name: "Elon Musk", kgCO2: 200 },
      { placing: 2, name: "Taylor Swift", kgCO2: 190 },
      { placing: 3, name: "Alan Sugar", kgCO2: 100 },
      { placing: 4, name: "kenn ich nicht", kgCO2: 80 },
      { placing: 5, name: "nicht echt", kgCO2: 1 },
    ],
  });
}

function Card() {
  const { totalLocationCO2KG, leaderboardContent } =
    useLoaderData<typeof loader>();

  return (
    <div className="flex w-full flex-col gap-3 lg:w-3/4 xl:w-2/3">
      <AirspaceCard totalCO2LocationKG={totalLocationCO2KG} />
      <div className="h-px w-11/12 self-center bg-zinc-700/20"></div>
      <LeaderboardCard leaderboardContent={leaderboardContent} />
    </div>
  );
}

export function ErrorBoundary() {
  const error = useRouteError();
  console.log(error);

  if (isRouteErrorResponse(error)) {
    return (
      <div className="flex flex-col justify-center text-xl text-slate-300 sm:text-3xl">
        <h1 className="text-center">
          {error.status} {error.statusText}
        </h1>
        <p>{error.data}</p>
      </div>
    );
  } else if (error instanceof Error) {
    return (
      <div>
        <h1>Error</h1>
        <p>{error.message}</p>
        <p>The stack trace is:</p>
        <pre>{error.stack}</pre>
      </div>
    );
  } else {
    return <h1>Unknown Error</h1>;
  }
}

export default Card;
