/* eslint-disable react/prop-types */

const TextArea = (props) => {
  // without handler
  let textarea = (
    <textarea
      type={props?.type}
      name={props?.name}
      cols={props?.cols}
      rows={props?.rows}
      value={props?.value}
      disabled={props?.disabled}
      className={props?.className}
      style={props?.style}
      placeholder={props?.placeholder}
    >
      {props?.children}
    </textarea>
  );

  // with handler
  if (props.onClick) {
    textarea = (
      <textarea
        type={props?.type}
        name={props?.name}
        cols={props?.cols}
        rows={props?.rows}
        value={props?.value}
        onClick={props?.onClick}
        disabled={props?.disabled}
        className={props?.className}
        style={props?.style}
        placeholder={props?.placeholder}
      >
        {props?.children}
      </textarea>
    );
  }

  return textarea;
};

export default TextArea;
