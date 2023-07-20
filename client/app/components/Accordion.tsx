import { useState } from "react";

export type AccordionItem = {
  title: string;
  content: string;
  links?: { title: string; link: string }[];
};

type Props = {
  items: AccordionItem[];
};

const Accordion = ({ items }: Props) => {
  const [activeIndices, setActiveIndices] = useState<number[]>([]);

  const handleToggle = (index: number) => {
    setActiveIndices((prevIndices) =>
      prevIndices.includes(index)
        ? prevIndices.filter((i) => i !== index)
        : [...prevIndices, index]
    );
  };

  return (
    <div className="w-full">
      {items.map((item, index) => (
        <div
          key={`${index} ${item.title}`}
          className="mb-6 rounded-b-lg rounded-t-lg bg-zinc-700 text-slate-200 hover:bg-zinc-600/75"
        >
          <div
            className={"flex cursor-pointer items-center justify-between p-4"}
            onClick={() => handleToggle(index)}
          >
            <span>{item.title}</span>
            <span>
              {activeIndices.includes(index) ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              )}
            </span>
          </div>
          {activeIndices.includes(index) && (
            <>
              <div className="whitespace-pre-line rounded-b-lg border-x-2 border-b-2 border-zinc-700 bg-zinc-800 p-4">
                {item.content}
                {item.links && (
                  <div className="flex gap-4">
                    {item.links.map((link) => (
                      <small
                        key={`${link.link} ${link.title}`}
                        className="pt-4 hover:cursor-pointer hover:underline"
                      >
                        <a target="_blank" href={link.link} rel="noreferrer">
                          {link.title}
                        </a>
                      </small>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
};

export default Accordion;
