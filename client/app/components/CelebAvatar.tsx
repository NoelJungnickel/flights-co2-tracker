type Props = {
  imgUrl?: string;
  name: string;
  border?: boolean;
  placing?: number;
  width?: number;
  height?: number;
};

function CelebAvatar({
  imgUrl,
  name,
  border = true,
  placing,
  height,
  width,
}: Props) {
  return (
    <div
      className={`relative ${height ? `h-${height}` : "h-52"} ${
        width ? `w-${width}` : "w-52"
      }`}
    >
      {imgUrl ? (
        <img
          className={`rounded-full ${border ? "border-2 border-white" : ""} ${
            width ? `w-${width}` : ""
          } text-sky-50 shadow-sm`}
          src={imgUrl}
          alt={name}
        />
      ) : null}
      {placing ? (
        <div className="z-2 absolute -bottom-6 left-0 right-0 ml-auto mr-auto h-12 w-12 rounded-full border-2 border-white bg-indigo-500 text-3xl font-medium text-white">
          <p className="flex h-full items-center justify-center ">{placing}</p>
        </div>
      ) : null}
    </div>
  );
}

export default CelebAvatar;
