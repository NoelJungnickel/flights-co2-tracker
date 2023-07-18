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
import { Line } from "react-chartjs-2";
import { CitiesData } from "~/routes/_app.stats.$city";
import { capitalizeFirstLetter } from "./AirspaceDropdownButton";

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
  const data: ChartData<"line"> = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: Object.keys(citiesData).map((city) => {
      const red = Math.floor(Math.random() * 255);
      const green = Math.floor(Math.random() * 255);
      const blue = Math.floor(Math.random() * 255);
      return {
        label: capitalizeFirstLetter(city),
        data: Array.from({ length: 7 }, () => Math.floor(Math.random() * 10)),
        borderColor: `rgb(${red}, ${green}, ${blue})`,
        backgroundColor: `rgba(${red}, ${green}, ${blue}, 0.5)`,
      };
    }),
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
