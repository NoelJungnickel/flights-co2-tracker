import { Outlet, isRouteErrorResponse, useRouteError } from "@remix-run/react";

function Stats() {
  return (
    <div className="flex max-h-fit min-h-screen justify-center bg-blue-200">
      <div className="flex w-3/4 py-4">
        <Outlet />
      </div>
    </div>
  );
}

export default Stats;
