import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
  type ChartData,
} from "chart.js";
import { CitiesData } from "~/routes/_app.stats.$city";
import { getChartProperties } from "~/utils/airspace_charting";
import { capitalizeFirstLetter } from "./AirspaceDropdownButton";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const CHART_FONT_COLOR = "#f0f9ff";

const options: ChartOptions<"line"> = {
  scales: {
    y: {
      title: {
        color: CHART_FONT_COLOR,
        display: true,
        text: "CO2 in tons",
      },
      ticks: {
        color: CHART_FONT_COLOR,
      },
      beginAtZero: true,
    },
    x: {
      ticks: {
        color: CHART_FONT_COLOR,
      },
    },
  },
  responsive: true,
  color: CHART_FONT_COLOR,
  animation: false,
  plugins: {
    legend: {
      position: "bottom" as const,
    },
    title: {
      display: true,
    },
  },
};

type Props = {
  citiesData: CitiesData;
};

function ChartCard({ citiesData }: Props) {
  const chartProperties = getChartProperties(citiesData);

  const data: ChartData<"line"> = {
    labels: chartProperties.labels.map((timestamp) => {
      return new Date(timestamp * 1000).toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
      });
    }),
    datasets: chartProperties.chartDatasets.map((dataset) => ({
      label: capitalizeFirstLetter(dataset.label),
      data: dataset.data,
      borderColor: dataset.borderColor,
      backgroundColor: dataset.backgroundColor,
    })),
  };

  return (
    <div className="h-fit w-full rounded-lg bg-zinc-700 py-5">
      <div className="flex w-full justify-center gap-3">
        <h1 className="text-center text-3xl font-bold text-sky-50">
          Airspace Chart
        </h1>
      </div>
      <div className="relative h-full w-full px-6 py-2 text-sky-50">
        <Line options={options} data={data} />
      </div>
    </div>
  );
}

export default ChartCard;
