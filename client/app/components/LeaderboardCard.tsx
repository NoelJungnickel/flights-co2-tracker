import { celebPicturesURL } from "~/utils/celeb_pics_url";
import CelebAvatar from "./CelebAvatar";

export type LeaderboardEntry = {
  placing: number;
  name: string;
  kgCO2: number;
};

type Props = {
  leaderboardContent: LeaderboardEntry[];
};

function LeaderboardCard({ leaderboardContent }: Props) {
  const ascendingSortedLeaderboard = leaderboardContent.sort(
    (a, b) => a.placing - b.placing
  );

  return (
    <div className="h-fit w-full rounded-lg bg-zinc-700 py-5">
      <div className="flex w-full flex-col justify-center gap-3 pb-6">
        <h1 className="pb-6 text-center text-4xl font-bold text-sky-50">
          Top 3 Emitters
        </h1>
        <div className="flex w-full justify-center gap-20">
          {[
            ascendingSortedLeaderboard[1],
            ascendingSortedLeaderboard[0],
            ascendingSortedLeaderboard[2],
          ].map((celeb, index) => {
            const celebPicture = celebPicturesURL.find(
              (celebPicture) => celebPicture.name === celeb.name
            );

            return (
              <div key={celeb.name} className="flex flex-col justify-end">
                <CelebAvatar
                  name={celeb.name}
                  imgUrl={celebPicture?.url}
                  placing={celeb.placing}
                  height={index !== 1 ? 44 : 52}
                  width={index !== 1 ? 44 : 52}
                />
                <div className="flex flex-col gap-2 pt-8">
                  <h1 className="text-center text-xl font-bold text-blue-50">
                    {celeb.name}
                  </h1>
                  <h2 className="text-center text-xl font-bold text-slate-300">
                    {celeb.kgCO2}
                    <span className="text-sm">kg</span>
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
