import { useEffect, useRef, useState } from "react";
import { type AirspaceOption } from "./AirspaceCard";

type Props = {
  options: AirspaceOption[];
  defaultOption: AirspaceOption;
  onSelect: (option: AirspaceOption) => void;
};

function AirspaceDropdownButton({ options, defaultOption, onSelect }: Props) {
  const [selectedOption, setSelectedOption] = useState(defaultOption);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleOptionSelect = (option: AirspaceOption) => {
    setSelectedOption(option);
    onSelect(option);
    setIsOpen(false);
  };

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      dropdownRef.current &&
      !dropdownRef.current.contains(event.target as Node)
    ) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    window.addEventListener("click", handleClickOutside);

    return () => {
      window.removeEventListener("click", handleClickOutside);
    };
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <div>
        <button
          type="button"
          className="inline-flex w-full justify-center rounded-md bg-sky-500 px-4 py-2 text-sm font-medium text-sky-50 focus:outline-none focus:ring-1 focus:ring-sky-50"
          id="dropdown-menu-button"
          onClick={toggleDropdown}
        >
          {selectedOption}
          <svg
            className="-mr-1 ml-2 h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path fillRule="evenodd" d="M10 12l-6-6h12l-6 6z" />
          </svg>
        </button>
      </div>
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 origin-top-right rounded-md bg-sky-500 shadow-lg ring-1 ring-black ring-opacity-5 md:left-0">
          <div
            role="menu"
            aria-orientation="vertical"
            aria-labelledby="dropdown-menu-button"
          >
            {options.map((option) => (
              <button
                key={option}
                className={`${
                  option === selectedOption
                    ? "bg-sky-600 hover:bg-sky-600 hover:text-sky-50"
                    : "hover:bg-gray-300 hover:text-gray-900"
                } block w-full rounded-md px-4 py-3 text-left text-sm text-sky-50`}
                role="menuitem"
                onClick={() => handleOptionSelect(option)}
                disabled={option === selectedOption}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AirspaceDropdownButton;
