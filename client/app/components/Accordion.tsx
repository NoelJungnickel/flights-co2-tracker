import { useState } from "react";

type AccordionItem = {
  title: string;
  content: string;
};

type Props = {
  items: AccordionItem[];
};

const Accordion = ({ items }: Props) => {
  const [activeIndex, setActiveIndex] = useState<null | number>(null);

  const handleToggle = (index: number) => {
    setActiveIndex(index === activeIndex ? null : index);
  };

  return (
    <div className="w-full">
      {items.map((item, index) => (
        <div
          key={index}
          className="mb-6 rounded-b-lg rounded-t-lg bg-zinc-700 text-slate-200 hover:bg-zinc-600/75"
        >
          <div
            className={"flex cursor-pointer items-center justify-between p-4"}
            onClick={() => handleToggle(index)}
          >
            <span>{item.title}</span>
            <span>
              {activeIndex === index ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
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
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              )}
            </span>
          </div>
          {activeIndex === index && (
            <div className="whitespace-pre-line rounded-b-lg border-x-2 border-b-2 border-zinc-700 bg-zinc-800 p-4">
              {item.content}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Accordion;
