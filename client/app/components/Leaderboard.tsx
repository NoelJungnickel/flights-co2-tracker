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
              <div className="flex items-center space-x-4">
                <p
                  className={`${fontSizeClass} truncate font-medium text-gray-900 dark:text-white`}
                >
                  {leaderboardEntry.placing}.
                </p>
                <div className="min-w-0 flex-1">
                  <p
                    className={`${fontSizeClass} truncate font-medium text-gray-900 dark:text-white`}
                  >
                    {leaderboardEntry.name}
                  </p>
                </div>
                <div
                  className={`${fontSizeClass} dark:text-whitez inline-flex items-center text-base font-semibold text-gray-900 dark:text-white`}
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
