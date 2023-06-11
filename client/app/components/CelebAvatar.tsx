type Props = {
  imgUrl: string;
  name: string;
  border?: boolean;
  placing?: number;
};

function CelebAvatar({ imgUrl, name, border = true, placing }: Props) {
  return (
    <div className="relative h-52 w-52">
      <img
        className={`rounded-full ${
          border ? "border-2 border-white" : ""
        } shadow-sm`}
        src={imgUrl}
        alt={name}
      />
      {placing ? (
        <div className="z-2 absolute -bottom-6 left-0 right-0 ml-auto mr-auto h-12 w-12 rounded-full border-2 border-white bg-indigo-500 text-3xl font-medium text-white">
          <p className="flex h-full items-center justify-center ">{placing}</p>
        </div>
      ) : null}
    </div>
  );
}

export default CelebAvatar;
