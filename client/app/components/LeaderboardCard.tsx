import { celebPicturesURL } from "~/utils/celeb_pics_url";
import CelebAvatar from "./CelebAvatar";
import type { CelebLeaderboard } from "~/routes/_app.stats.$city";

type Props = {
  leaderboardContent: CelebLeaderboard;
};

function LeaderboardCard({ leaderboardContent }: Props) {
  const ascendingSortedLeaderboard = leaderboardContent.sort(
    (a, b) => b.emissionsInKg - a.emissionsInKg
  );

  return (
    <div className="h-fit w-full rounded-lg bg-zinc-700 py-5">
      <div className="flex w-full flex-col justify-center gap-3 pb-6">
        <h1 className="px-1 pb-6 text-center text-4xl font-bold text-sky-50">
          Top 3 CO2 Emitters of the Last 30 Days
        </h1>
        <div className="flex w-full flex-col justify-center gap-10 sm:flex-row sm:gap-6 md:gap-20">
          {[
            ascendingSortedLeaderboard[0],
            ascendingSortedLeaderboard[1],
            ascendingSortedLeaderboard[2],
          ].map((celeb, index) => {
            const celebPicture = celebPicturesURL.find(
              (celebPicture) => celebPicture.name === celeb.name
            );

            return (
              <div
                key={celeb.name}
                className={`${
                  index === 1 ? "sm:order-overwrite-first" : ""
                } flex flex-col justify-end`}
              >
                <CelebAvatar
                  name={celeb.name}
                  imgUrl={celebPicture?.url}
                  placing={index + 1}
                />
                <div className="flex flex-col gap-2 pt-8">
                  <h1 className="text-center text-xl font-bold text-blue-50">
                    {celeb.name}
                  </h1>
                  <h2 className="text-center text-xl font-bold text-slate-300">
                    {Math.floor(celeb.emissionsInKg / 1000)}
                    <span className="text-sm">t</span>
                  </h2>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default LeaderboardCard;
