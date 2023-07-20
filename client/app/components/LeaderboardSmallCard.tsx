import type { CelebLeaderboardEntry } from "~/routes/_app.stats.$city";
import { celebPicturesURL } from "~/utils/celeb_pics_url";

type Props = {
  celebLeaderboardEntry: CelebLeaderboardEntry;
  placing: number;
};

function LeaderboardSmallCard({ celebLeaderboardEntry, placing }: Props) {
  const celebPicture = celebPicturesURL.find(
    (celebPicture) => celebPicture.name === celebLeaderboardEntry.name
  );

  return (
    <a
      target="_blank"
      href={`https://en.wikipedia.org/wiki/${celebLeaderboardEntry.name
        .trim()
        .replace(" ", "_")}`}
      className="hover:cursor-pointer"
    >
      <div className="flex justify-center font-normal text-blue-50">
        <div className="flex w-full items-center justify-between divide-x-2 divide-zinc-800/30 rounded-lg bg-zinc-700 py-2 text-xl hover:translate-x-1 sm:w-11/12">
          <div className="flex-3 px-4 sm:px-7">
            <div className="h-8 w-8 rounded-full bg-indigo-500">
              <h1 className="flex h-full items-center justify-center">
                {placing}
              </h1>
            </div>
          </div>
          <div className="flex flex-1 gap-3 px-4 sm:gap-6 sm:px-6">
            <img
              className="h-20 rounded-full border-2 border-white"
              src={celebPicture?.url}
              alt={`${celebPicture?.name}`}
            />
            <h1 className="self-center text-lg sm:text-2xl">
              {celebLeaderboardEntry.name}
            </h1>
          </div>
          <div className="flex-2 flex h-full min-w-[75px] items-center px-3 sm:min-w-[100px] sm:px-6">
            <h2 className="w-full text-center text-2xl font-bold">
              {Math.floor(celebLeaderboardEntry.emissionsInKg / 1000)}
              <span className="text-xl">t</span>
            </h2>
          </div>
        </div>
      </div>
    </a>
  );
}

export default LeaderboardSmallCard;
