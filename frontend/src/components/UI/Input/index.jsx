/* eslint-disable react/prop-types */

const Input = (props) => {
  // without handler
  let input = (
    <input
      type={props?.type}
      name={props?.name}
      disabled={props?.disabled}
      className={props?.className}
      style={props?.style}
      value={props?.value}
      placeholder={props?.placeholder}
      autoComplete="off"
      autoCapitalize="off"
    >
      {props?.children}
    </input>
  );

  // with handler
  if (props.onClick) {
    input = (
      <input
        type={props?.type}
        name={props?.name}
        className={props?.className}
        onClick={props?.onClick}
        value={props?.value}
        style={props?.style}
        disabled={props?.disabled}
        placeholder={props?.placeholder}
        autoComplete="off"
        autoCapitalize="off"
      >
        {props?.children}
      </input>
    );
  }
  return input;
};

export default Input;
