/* eslint-disable react/prop-types */
const Spinner = ({ styles }) => {
  return (
    <div
      className={`inline-block animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] text-info motion-reduce:animate-[spin_1.5s_linear_infinite] ${styles}`}
      role="status"
    ></div>
  );
};

export default Spinner;
