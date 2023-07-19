import type { ActionArgs, LoaderArgs, TypedResponse } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  isRouteErrorResponse,
  useLoaderData,
  useRouteError,
} from "@remix-run/react";
import type { AirspaceOption } from "~/components/AirspaceCard";
import AirspaceCard, { airspaceOptions } from "~/components/AirspaceCard";
import ChartCard from "~/components/ChartCard";
import LeaderboardCard from "~/components/LeaderboardCard";
import LeaderboardSmallCard from "~/components/LeaderboardSmallCard";

type Stats = {
  location: AirspaceOption;
  totalLocationCO2KG: number;
  leaderboardContent: CelebLeaderboard;
  serverstart: number;
  citiesData: CitiesData;
};

type AirspaceCarbonResponse = {
  airspace_name: string;
  total: number;
};

type CelebLeaderboardResponse = {
  [key: string]: number;
};

export type CelebLeaderboardEntry = {
  name: string;
  emissionsInKg: number;
};

export type CelebLeaderboard = CelebLeaderboardEntry[];

type ServerStart = {
  timestamp: number;
};

type CitiesDataResponse = {
  airspace_name: string;
  data: {
    [key: string]: number;
  };
};

export type CitiesData = {
  [city: string]: {
    [timestamp: string]: number;
  };
};

function decapitalizeFirstLetter(word: string) {
  return word.charAt(0).toLowerCase() + word.slice(1);
}

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
  const celebLeaderboardResponse = await fetch(`${API_URL}/leaderboard`);
  const serverstartResponse = await fetch(`${API_URL}/serverstart`);

  if (!totalCO2KgReponse || !celebLeaderboardResponse || !serverstartResponse) {
    throw new Response("Internal Server Error", {
      status: 500,
    });
  }

  const totalCO2Kg = (await totalCO2KgReponse.json()) as AirspaceCarbonResponse;
  const serverstart = (await serverstartResponse.json()) as ServerStart;
  const { timestamp: serverstartTimestamp } = serverstart;

  const celebLeaderboardObject =
    (await celebLeaderboardResponse.json()) as CelebLeaderboardResponse;
  const celebLeaderboard = Object.entries(
    celebLeaderboardObject.celeb_emission
  ).map(([name, emissions]) => ({
    name,
    emissionsInKg: emissions,
  }));

  const citiesDataPromises = airspaceOptions.map(async (city) => {
    const response = await fetch(
      `${API_URL}/${decapitalizeFirstLetter(city)}/data`
    );
    const data = (await response.json()) as CitiesDataResponse;
    return data;
  });
  const citiesDataReponse = await Promise.all(citiesDataPromises);
  const citiesData = citiesDataReponse.reduce((acc, item) => {
    acc[item.airspace_name] = item.data;
    return acc;
  }, {} as CitiesData);

  return json({
    location: city! as AirspaceOption,
    totalLocationCO2KG: totalCO2Kg.total,
    serverstart: serverstartTimestamp,
    leaderboardContent: celebLeaderboard,
    citiesData,
  });
}

function Card() {
  const {
    location,
    totalLocationCO2KG,
    leaderboardContent,
    serverstart,
    citiesData,
  } = useLoaderData<typeof loader>();

  console.log(citiesData);

  return (
    <div className="flex w-full flex-col gap-3 pt-6 lg:w-3/4 xl:w-2/3">
      <AirspaceCard
        serverstart={serverstart}
        location={location}
        totalCO2LocationKG={totalLocationCO2KG}
      />
      <div className="h-px w-11/12 self-center bg-zinc-700/20"></div>
      <ChartCard citiesData={citiesData} />
      <div className="h-px w-11/12 self-center bg-zinc-700/20"></div>
      <LeaderboardCard leaderboardContent={leaderboardContent} />
      <div className="flex w-full items-center justify-center py-8">
        <h1 className="relative min-h-[50px] w-fit text-center text-4xl font-bold text-sky-50">
          Leaderboard
          <svg
            width="50"
            height="50"
            viewBox="0 0 50 50"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="absolute -right-16 -top-2"
          >
            <path
              d="M8.33341 39.5833H16.6667V22.9167H8.33341V39.5833ZM20.8334 39.5833H29.1667V10.4167H20.8334V39.5833ZM33.3334 39.5833H41.6667V27.0833H33.3334V39.5833ZM4.16675 43.75V18.75H16.6667V6.25H33.3334V22.9167H45.8334V43.75H4.16675Z"
              fill="#F0F9FF"
            />
          </svg>
        </h1>
      </div>
      {leaderboardContent
        .sort((a, b) => b.emissionsInKg - a.emissionsInKg)
        .slice(3)
        .map((leaderboardEntry, index) => {
          if (leaderboardEntry.emissionsInKg <= 0) {
            return null;
          }

          return (
            <LeaderboardSmallCard
              celebLeaderboardEntry={leaderboardEntry}
              placing={index + 4}
              key={`${leaderboardEntry.name}-${leaderboardEntry.emissionsInKg}`}
            />
          );
        })}
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
      <div className="text-slate-300">
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
