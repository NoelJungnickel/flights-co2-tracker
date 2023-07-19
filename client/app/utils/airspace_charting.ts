import type { CitiesData } from "~/routes/_app.stats.$city";

// const data: {
//   [city: string]: {
//     [timestamp: string]: number;
//   };
// } = {
//   berlin: {
//     "1689529853": 9609.197462575434,
//     "1689533453": 20314.847503568377,
//     "1689540202": 28890.227990984033,
//     "1689604327": 46452.99835372659,
//     "1689607928": 58844.296625874355,
//     "1689612348": 67715.73875851143,
//     "1689615947": 80526.65284338291,
//     "1689620698": 92311.24408381645,
//     "1689624566": 92623.84858861429,
//     "1689628165": 111794.17205061918,
//   },
//   london: {
//     "1689529853": 54469.15383469771,
//     "1689533453": 116725.58015957428,
//     "1689540202": 155446.3999584968,
//     "1689545025": 158667.82612928684,
//     "1689604327": 211180.8967495851,
//     "1689607928": 277030.90477097296,
//     "1689612348": 312574.6854943187,
//     "1689615947": 344983.5785010062,
//     "1689620698": 384193.5825499934,
//     "1689624566": 389648.11319774436,
//     "1689628165": 431954.46111536573,
//     "1689631766": 467220.42521644285,
//   },
//   madrid: {
//     "1689529853": 7971.927160220213,
//     "1689533453": 16576.500553256694,
//     "1689540202": 20817.302894231205,
//     "1689545025": 21313.252894231206,
//     "1689550291": 21539.732894231205,
//     "1689604327": 33512.660100419045,
//     "1689607928": 44782.90927489437,
//     "1689612348": 48598.19244610842,
//     "1689615947": 55173.66065462762,
//     "1689620698": 56657.43576683995,
//     "1689624566": 57045.235766839956,
//     "1689628165": 66201.58241856073,
//     "1689631766": 71451.57426118641,
//   },
//   paris: {},
// };

export const SECONDS_IN_DAY = 86400;

export function getStartOfDayTimestamp(timestamp: number) {
  const date = new Date(timestamp * 1000);
  date.setHours(0, 0, 0, 0);

  return Math.floor(date.getTime() / 1000);
}

export function getDayCountFromTimestamps(
  timestamp1: number,
  timestamp2: number
) {
  const millisecondsPerDay = 24 * 60 * 60 * 1000;

  const date1 = new Date(timestamp1 * 1000);
  const date2 = new Date(timestamp2 * 1000);
  date1.setHours(0, 0, 0, 0);
  date2.setHours(0, 0, 0, 0);

  const timeDifference = Math.abs(date2.getTime() - date1.getTime());
  const daysDifference = Math.ceil(timeDifference / millisecondsPerDay);

  return daysDifference + 1;
}

export function getDataPointsForDays(
  citiesData: CitiesData,
  dayFirstSecond: number,
  daysAmount: number
) {
  const dataPoints: Record<string, number[]> = {};

  for (let dayCount = 0; dayCount < daysAmount; dayCount++) {
    const dayLastSecond = dayFirstSecond + (SECONDS_IN_DAY - 1);

    for (const city in citiesData) {
      if (!dataPoints.hasOwnProperty(city)) {
        dataPoints[city] = [];
      }

      let maxTimestamp = 0;
      for (const timestampString in citiesData[city]) {
        const timestamp = parseInt(timestampString);
        if (timestamp > 0 && timestamp <= dayLastSecond) {
          maxTimestamp = timestamp;
        }
      }

      dataPoints[city].push(citiesData[city][maxTimestamp]);
    }

    dayFirstSecond = dayLastSecond + 1;
  }

  return dataPoints;
}

export function getSharedOldestAndLatestTimestamp(citiesData: CitiesData) {
  const timestampCounts: Record<string, number> = {};

  for (const city in citiesData) {
    const cityData = citiesData[city];
    for (const timestamp in cityData) {
      if (timestampCounts.hasOwnProperty(timestamp)) {
        timestampCounts[timestamp]++;
      } else {
        timestampCounts[timestamp] = 1;
      }
    }
  }

  const amountOfNonEmptyKeys = Object.keys(citiesData).filter(
    (key) =>
      citiesData[key] !== undefined && Object.keys(citiesData[key]).length !== 0
  ).length;

  let lowestTimestamp = Infinity;
  let highestTimestamp = -Infinity;

  for (const timestampString in timestampCounts) {
    const timestamp = parseInt(timestampString);
    if (timestampCounts[timestamp] !== amountOfNonEmptyKeys) {
      continue;
    }

    if (timestamp < lowestTimestamp) {
      lowestTimestamp = timestamp;
    }
    if (timestamp > highestTimestamp) {
      highestTimestamp = timestamp;
    }
  }

  return [lowestTimestamp, highestTimestamp];
}

function hashStringToRGB(str: string) {
  let hash = 0;

  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  const r = (hash & 0xff0000) >> 16;
  const g = (hash & 0x00ff00) >> 8;
  const b = hash & 0x0000ff;

  return [r, g, b];
}

export function getChartProperties(citiesData: CitiesData) {
  const [sharedOldestTimestamp] = getSharedOldestAndLatestTimestamp(citiesData);
  const currentTimestamp = Math.floor(Date.now() / 1000);

  const dayFirstSecond = getStartOfDayTimestamp(sharedOldestTimestamp);
  const daysBetweenCount = getDayCountFromTimestamps(
    sharedOldestTimestamp,
    currentTimestamp
  );
  const datapoints = getDataPointsForDays(
    citiesData,
    dayFirstSecond,
    daysBetweenCount
  );

  const labels = Array.from(
    Array(daysBetweenCount),
    (_, num) => dayFirstSecond + SECONDS_IN_DAY * num
  );

  const chartDatasets = [];
  for (const datapoint in datapoints) {
    const [red, green, blue] = hashStringToRGB(datapoint);

    chartDatasets.push({
      label: datapoint,
      data: Array.from(datapoints[datapoint], (_, i) => {
        const co2KgValue = datapoints[datapoint][i] ?? 0;
        return Math.floor(co2KgValue / 1000);
      }),
      borderColor: `rgb(${red}, ${green}, ${blue})`,
      backgroundColor: `rgba(${red}, ${green}, ${blue}, 0.5)`,
    });
  }

  return { labels, chartDatasets };
}
