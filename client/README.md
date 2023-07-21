# Flights-CO2-Tracker Remix Frontend

This directory contains the frontend of the Flights CO2 Tracker and is designed to be hosted on Vercel. The frontend is currently hosted at https://flights-co2-tracker.vercel.app/.
For the seamless developer experience and server-side rendering, we use the React Meta-Framework Remix.

At the moment, we display carbon emissions within the airspaces of Berlin, Paris, London and Madrid and for a handful of celebrities defined in `app/utils/celeb_pics_url`.

## General Code Structure

The frontend consists of the following files:

- `app` directory containing routing, components, utils, and styles:
  - `root.tsx`: Contains the main wrapping html skeleton for the whole app. It initializes the tailwind styles, fonts, as well as the ability to add meta- and script tags on a per page basis with the help of remix helper functions.
  - `entry.[client, server].tsx`: Auto generated files by Remix handling the server-side rendering functionality and hydrating the page accordingly.
  - `routes/_index.tsx`: The page-component for the "_/_" route, it handles the redirection to "_/stats/berlin_" and has text with some styling indicating that the user is supposed to be redirected to "_/stats/berlin_".
  - `routes/_app.tsx`: A page-component wrapping every other file beginning with "_app_". It provides the header as well as the footer. It also adds basic styling to the main content which is inserted into the wrapper.
  - `routes/_app.stats.$city.tsx`: The main page-component of the website which lives on the "_/stats/{city}_" route and fetches all the data of a city based on the url and reformats it according to the expectations of the page-component and all child components. It displays basic CO2 airspace stats, a chart containing those stats on a daily basis, and a celebrity leaderboard by using the components _LeaderboardCard_ and _LeaderboardSmallCard_, as well as _AirspaceCard_ and _ChartCard_.
  - `routes/_app.faq.tsx`: A page-component displaying predefined questions and answers via the Accordion component.
  - `components/Accordion.tsx`: A component that takes Accordion items as props and displays them in the classic Accordion style.
  - `components/AirspaceCard.tsx`: A component displaying the total CO2 emitted into the a given airspace by airplanes since serverstart. It also contains the AirspaceDropdownButton component giving the ability to switch the wanted airspace.
  - `components/AirspaceDropdownButton.tsx`: A component displaying a dropdown-button which gives the ability for the user to select an airspace.
  - `components/CelebAvatar.tsx`: A component that displays a round avatar with a circled number underneath indicating a top 3 placing in the leaderboard.
  - `components/ChartCard.tsx`: A component charting the daily CO2 emissions in all provided airspaces powered by _Chart.js_ and the react wrapper package _react-chartjs-2_.
  - `components/Footer.tsx`: A component displaying the footer of the website which contains information about contributors as well as the technology that makes this project possible.
  - `components/Header.tsx`: A component displaying the header of the website which contains the title and a button which either routes to the stats or the FAQ based on the current route.
  - `components/LeaderboardCard.tsx`: This component displays the top 3 CO2 emitting celebrities caused by their private jets. It utilizes the _CelebAvatar_ component to display them neatly.
  - `components/LeaderboardSmallCard.tsx`: A component which displays a celebrities name, their placing, and their CO2 emissions amount in a rectangular card. This component is being being mapped over in \__app.stats.$city_ for every celebrity with a placing larger than 3.
  - `components/LoadingSpinner.tsx`: This component is just a simple neat looking loading spinner for indicating loading state.
  - `utils/airspace_charting.ts`: This file contains several functions that help with processing the data coming from the backend into a format useable for the frontend.
  - `utils/celeb_pics_url.ts`: This file exports the list celebPicturesURL containing objects with the fields name and url. This list is being used to map the celebrity names coming from the backend to their respective pictures on the frontend.
  - `tailwind.css`: The file enabling tailwind inline css classes to work.
- `api` directory containing auto-generated JavaScript files defining the server responsible for server-side rendering.
- `public` directory containing the favicon for the website.
- `reset.d.ts`: This file is mandatory for ts-reset to work.
- `remix.config.js` defines build paths, enables tailwind and v2 features of remix
- `server.ts`: Initializes the Remix server responsible for server-side rendering
- `tailwind.config.ts`: Config file for tailwind defining fonts and which files tailwind should detect.
- `tsconfig.json`: Config file for TypeScript enabling very strict typing rules ensuring safer code, as well as a better developer experience

## Run The Website locally

### Using npm

Make sure you are in the `client` directory

```zsh
cd client
```

Install all necessary packages

```zsh
npm i
```

Start the local development server

```zsh
npm run dev
```

Open up [http://localhost:3000](http://localhost:3000) and you should be ready to go!

Other scripts that can be run via `npm run` include:

`build` for building the website for production

`typecheck` for running the TypeScript typechecker

`format` for manual local formatting via Prettier

`lint` for manual local TypeScript code linting
