import { json } from "@remix-run/node";
import {
  isRouteErrorResponse,
  useLoaderData,
  useRouteError,
} from "@remix-run/react";
import { useState } from "react";
import Berlin from "~/components/Berlin";
import FAQ from "~/components/FAQ";
import Leaderboard, { LeaderboardEntry } from "~/components/Leaderboard";

type Stats = {
  totalCO2BerlinKG: number;
  leaderboardContent: LeaderboardEntry[];
};

enum Tab {
  berlin,
  leaderboard,
  faq,
}

export async function loader(): Promise<Stats> {
  return {
    totalCO2BerlinKG: 2000,
    leaderboardContent: [
      { placing: 1, name: "Aryeh Schöfer", kgCO2: 200 },
      { placing: 2, name: "Noel Jungnickel", kgCO2: 190 },
      { placing: 3, name: "cool name", kgCO2: 100 },
      { placing: 4, name: "kenn ich nicht", kgCO2: 80 },
      { placing: 5, name: "nicht echt", kgCO2: 1 },
    ],
  };
}

function Card() {
  const { totalCO2BerlinKG, leaderboardContent } =
    useLoaderData<typeof loader>();
  console.log(leaderboardContent);

  const [currentTab, setCurrentTab] = useState(Tab.berlin);

  const activeTabStyle =
    "inline-block w-full p-4 text-blue-600 dark:text-blue-500 bg-gray-50 hover:bg-gray-100 focus:outline-none dark:bg-gray-700 dark:hover:bg-gray-600";
  const unactiveTabStyle =
    "inline-block w-full p-4 bg-gray-50 hover:bg-gray-100 focus:outline-none dark:bg-gray-700 dark:hover:bg-gray-600";

  return (
    <div className="w-full rounded-lg bg-white shadow dark:bg-gray-800">
      <div className="flex rounded bg-white dark:bg-gray-700 sm:hidden">
        <select
          onChange={({
            target: { value },
          }: React.ChangeEvent<HTMLSelectElement> & {
            target: { value: "Berlin" | "Top 10" | "FAQ" };
          }) => {
            const newTab =
              value === "Berlin"
                ? Tab.berlin
                : value === "Top 10"
                ? Tab.leaderboard
                : Tab.faq;
            setCurrentTab(newTab);
          }}
          className="block w-full appearance-none rounded-t-lg border-gray-200 bg-gray-50 p-2.5 text-sm text-gray-900 outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        >
          <option>Berlin</option>
          <option>Top 10</option>
          <option>FAQ</option>
        </select>
        <div className="flex">
          <svg className="self-center fill-white" height="10px" width="20px">
            <path d="M5.952 6.97c-.268 0-.525-.106-.714-.294L.355 1.802C-.04 1.408-.04.772.355.378c.394-.393 1.032-.393 1.427 0l4.17 4.162 4.17-4.162c.394-.393 1.032-.393 1.426 0 .395.393.395 1.03 0 1.424L6.665 6.676c-.19.188-.445.295-.713.295z"></path>
          </svg>
        </div>
      </div>
      <ul
        className="hidden divide-x divide-gray-200 rounded-lg text-center text-sm font-medium text-gray-500 dark:divide-gray-600 dark:text-gray-400 sm:flex"
        role="tablist"
      >
        <li className="w-full">
          <button
            type="button"
            role="tab"
            className={`${
              currentTab == Tab.berlin ? activeTabStyle : unactiveTabStyle
            } rounded-tl-lg`}
            onClick={() => setCurrentTab(Tab.berlin)}
          >
            Berlin
          </button>
        </li>
        <li className="w-full">
          <button
            type="button"
            role="tab"
            className={
              currentTab == Tab.leaderboard ? activeTabStyle : unactiveTabStyle
            }
            onClick={() => setCurrentTab(Tab.leaderboard)}
          >
            Top 10
          </button>
        </li>
        <li className="w-full">
          <button
            type="button"
            role="tab"
            className={`${
              currentTab == Tab.faq ? activeTabStyle : unactiveTabStyle
            } rounded-tr-lg`}
            onClick={() => setCurrentTab(Tab.faq)}
          >
            FAQ
          </button>
        </li>
      </ul>
      <div className="border-t border-gray-200 dark:border-gray-600">
        <div
          className="flex flex-col gap-10 rounded-lg bg-white p-4 text-center dark:bg-gray-800 md:p-8"
          id="stats"
          role="tabpanel"
          aria-labelledby="stats-tab"
        >
          {currentTab === Tab.berlin ? (
            <Berlin totalCO2BerlinKG={totalCO2BerlinKG} />
          ) : currentTab === Tab.leaderboard ? (
            <Leaderboard leaderboardContent={leaderboardContent} />
          ) : (
            <FAQ />
          )}
        </div>
      </div>
    </div>
  );
}

export function ErrorBoundary() {
  const error = useRouteError();
  console.log(error);

  if (isRouteErrorResponse(error)) {
    return (
      <div>
        <h1>
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
