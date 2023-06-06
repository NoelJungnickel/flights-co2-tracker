export type LeaderboardEntry = {
  placing: number;
  name: string;
  kgCO2: number;
};

type Props = {
  leaderboardContent: LeaderboardEntry[];
};

function Leaderboard({ leaderboardContent }: Props) {
  const ascendingSortedLeaderboard = leaderboardContent.sort(
    (a, b) => a.placing - b.placing
  );

  return (
    <div className="flex justify-center">
      <ul className="w-2/3 max-w-lg divide-y divide-gray-200 dark:divide-gray-700">
        {ascendingSortedLeaderboard.map((leaderboardEntry) => {
          const fontSizeClass =
            leaderboardEntry.placing !== 1 ? "text-lg" : "text-3xl";
          return (
            <li key={leaderboardEntry.placing} className="py-3 sm:py-4">
              <div className="flex flex-col sm:flex-row">
                <div
                  className={`${fontSizeClass} pr-0 font-medium text-gray-900 dark:text-white sm:pr-10`}
                >
                  {leaderboardEntry.placing}.
                </div>
                <div
                  className={`${fontSizeClass} flex-1 text-center font-medium text-gray-900 dark:text-white sm:text-left`}
                >
                  {leaderboardEntry.name}
                </div>
                <div
                  className={`${fontSizeClass} font-semibold text-gray-900 dark:text-white `}
                >
                  {leaderboardEntry.kgCO2} kg CO2
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Leaderboard;
