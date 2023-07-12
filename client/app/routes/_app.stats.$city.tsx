import type { ActionArgs, LoaderArgs, TypedResponse } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  Outlet,
  isRouteErrorResponse,
  useLoaderData,
  useRouteError,
} from "@remix-run/react";
import type { AirspaceOption } from "~/components/AirspaceCard";
import AirspaceCard from "~/components/AirspaceCard";
import type { LeaderboardEntry } from "~/components/LeaderboardCard";
import LeaderboardCard from "~/components/LeaderboardCard";

type Stats = {
  location: AirspaceOption;
  totalLocationCO2KG: number;
  leaderboardContent: LeaderboardEntry[];
  serverstart: number;
};

type AirspaceCarbonResponse = {
  airspace_name: string;
  total: number;
};

type ServerStart = {
  timestamp: number;
};

export async function action({ request }: ActionArgs) {
  const body = await request.formData();
  const data = Object.fromEntries(body);
  const { option } = data;
  console.log(option);
  return redirect(`/stats/${option}`);
}

export async function loader({
  params,
}: LoaderArgs): Promise<TypedResponse<Stats>> {
  const { city } = params;
  let API_URL = `http://35.210.64.77:8000/api`;
  if (process.env.NODE_ENV === "development") {
    API_URL = `http://127.0.0.1:8000/api`;
  }

  const totalCO2KgReponse = await fetch(
    `${API_URL}/${city?.toLowerCase()}/total`
  );

  const serverstartResponse = await fetch(`${API_URL}/serverstart`);

  if (!totalCO2KgReponse) {
    throw new Response("Internal Server Error", {
      status: 500,
    });
  }

  const totalCO2Kg = (await totalCO2KgReponse.json()) as AirspaceCarbonResponse;
  const serverstart = (await serverstartResponse.json()) as ServerStart;
  const { timestamp } = serverstart;
  console.log(serverstart);

  return json({
    location: city! as AirspaceOption,
    totalLocationCO2KG: totalCO2Kg.total,
    serverstart: timestamp,
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
  const { location, totalLocationCO2KG, leaderboardContent, serverstart } =
    useLoaderData<typeof loader>();

  console.log(serverstart);
  return (
    <div className="flex w-full flex-col gap-3 lg:w-3/4 xl:w-2/3">
      <AirspaceCard
        serverstart={serverstart}
        location={location}
        totalCO2LocationKG={totalLocationCO2KG}
      />
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
