/* eslint-disable react/prop-types */

const Button = (props) => {
  // without handler
  let button = (
    <button
      type={props?.type}
      name={props?.name}
      disabled={props?.disabled}
      className={props?.className}
      style={props?.style}
    >
      {props?.children}
    </button>
  );

  // with handler
  if (props?.onClick) {
    button = (
      <button
        type={props?.type}
        name={props?.name}
        className={props?.className}
        onClick={props?.onClick}
        style={props?.style}
        disabled={props?.disabled}
      >
        {props?.children}
      </button>
    );
  }
  return button;
};

export default Button;
