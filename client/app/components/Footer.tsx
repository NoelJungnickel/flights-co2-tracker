function Footer() {
  return (
    <div className="flex w-full items-center justify-center bg-zinc-800 pb-4 text-center font-poppins text-slate-200">
      <small>
        Powered by{" "}
        <a
          href="https://cloud.google.com/"
          target="_blank"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Google Cloud
        </a>
        ,{" "}
        <a
          href="https://opensky-network.org/"
          target="_blank"
          className=" text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          OpenSky
        </a>
        ,{" "}
        <a
          href="https://remix.run/"
          target="_blank"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Remix
        </a>
        , and{" "}
        <a
          target="_blank"
          href="https://vercel.com/"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Vercel
        </a>{" "}
        | Made with ❤️ by{" "}
        <a
          target="_blank"
          href="https://github.com/AryehSchoefer"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Aryeh
        </a>
        ,{" "}
        <a
          target="_blank"
          href="https://github.com/NulliBulli"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Noel
        </a>
        ,{" "}
        <a
          target="_blank"
          href="https://github.com/kilianp14"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Paul
        </a>
        , and{" "}
        <a
          target="_blank"
          href="https://github.com/swinarga"
          className="text-zinc-400 hover:underline"
          rel="noreferrer"
        >
          Satya
        </a>
      </small>
    </div>
  );
}

export default Footer;
