const Error = ({ hasError, error, ...props }) => {
  const parseErrorMessage = (data) => {
    const msgStartIndex = data.indexOf('data-msg="') + 'data-msg="'.length;
    const msgEndIndex = data.indexOf('"', msgStartIndex);
    const msg = data
      .substring(msgStartIndex, msgEndIndex)
      .replace(/&quot;/g, '"');

    const stackStartIndex = data.indexOf('data-stck="') + 'data-stck="'.length;
    const stackEndIndex = data.indexOf('"', stackStartIndex);
    const stack = data
      .substring(stackStartIndex, stackEndIndex)
      .replace(/\\n/g, "\\n");
    console.error(msg, stack);
    return { msg, stack };
  };

  if (hasError) {
    const { msg, stack } = parseErrorMessage(error);
    return (
      <div className="fixed inset-0 flex items-center justify-center z-50">
        <div className="bg-white rounded-md shadow-lg p-8 max-w-screen-2xl w-full">
          <h2 className="text-lg font-semibold mb-2 text-red-600">Error</h2>
          <p className="mb-4 text-gray-800">{msg}</p>
          <pre className="bg-red-100 p-4 rounded overflow-x-auto text-red-700">
            {stack}
          </pre>
        </div>
      </div>
    );
  } else {
    return <>{props.children}</>;
  }
};
