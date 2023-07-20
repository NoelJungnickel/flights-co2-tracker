import Accordion from "~/components/Accordion";

function Faq() {
  const questions = [
    {
      title: "What is the goal of this page?",
      content: "Content of Section 1",
    },
    {
      title: "Where does the data come from?",
      content: "Content of Section 2",
    },
    {
      title: "How accurate is the data?",
      content: "Content of Section 2",
    },
    {
      title: "How often does the data update?",
      content: "Content of Section 2",
    },
    {
      title: "How does the data compare?",
      content: "Content of Section 2",
    },
  ];

  return (
    <div className="w-full lg:w-2/3">
      <Accordion items={questions} />
    </div>
  );
}
export default Faq;
