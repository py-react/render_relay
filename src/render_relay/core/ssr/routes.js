import { Writable, Transform } from "stream";
import { resolve as _resolve } from "path";
const ext = "js";

import { createElement as _createElement } from "react";
import { renderToPipeableStream } from "react-dom/server";


class LoggingTransformStream extends Transform {
  constructor(options) {
    super(options);
  }

  _transform(chunk, encoding, callback) {
    // Check if chunk is undefined
    if (typeof chunk === 'undefined') {
      console.error("Received undefined chunk");
      // Call the callback to signal that the chunk has been processed
      return callback();
    }

    // Pass the chunk through to the next stream in the pipeline
    this.push(chunk);
    // Call the callback to signal that the chunk has been processed
    callback();
  }

}

// Custom writable stream that logs data to the console
class LoggingWritableStream extends Writable {
  constructor(options) {
    super(options);
    this.data = [];
  }

  renderString() {
    return this.data.join("");
  }

  _write(chunk, encoding, callback) {
    this.data.push(chunk.toString());
    // Call the callback to signal that the chunk has been processed
    callback();
  }
}

class SSR {
  constructor(cwd) {
    this.cwd = cwd
  }
  async render(props) {
    return new Promise(async(resolve, reject) => {
      try {
        const App = await import(_resolve("./","_gingerjs", "build", "_gingerjs","__build__", "app.js"));
        const StaticRouter = await import(_resolve(
          "./",
          "_gingerjs",
          "build",
          "_gingerjs","__build__",
          "StaticRouterWrapper.js"
        ));
        const {getAppContext} = await import(_resolve(
          "./",
          "_gingerjs",
          "build",
          "app",
          "layout.js"
        ));
        const { location } = props;
        const ReactElement = _createElement(App.default, {
          children: null,
          location,
          ...props,
        });
        const StaticRouterWrapper = _createElement(StaticRouter.default, {
          children: ReactElement,
          url: props.location.path,
        });
        const providedCtx = {
          app:StaticRouterWrapper,
          renderApp:()=>({
            enhanceApp:(App)=>App,
            getStyles:(App)=>App,
            styles:()=>"",
            finally:()=>{}
          })
        }
        const renderApp = (render)=>{
          const rendered = render.renderApp();
          const componentHTML =
            renderToPipeableStream(rendered.getStyles(StaticRouterWrapper));
          
          // Create an instance of the logging writable stream
          const loggingWritableStream = new LoggingWritableStream();
          const loggingTransformStream = new LoggingTransformStream();
          componentHTML.pipe(loggingTransformStream).pipe(loggingWritableStream);
          // After the stream has ended, the concatenated string can be accessed
          loggingWritableStream.on("finish", () => {
            resolve(loggingWritableStream.renderString().concat(rendered.styles()))
            rendered.finally()
          });
        }
        if(typeof getAppContext === "function"){
          Object.assign(providedCtx, await getAppContext(providedCtx));
        }
        renderApp(providedCtx)

      } catch (error) {
        console.log(error,"error")
        reject(error);
      }
    })
  }
  
 // beta
  async partialRender(props){
    return new Promise((resolve, reject) => {
      // const Component = require(path.resolve("./", "build", "app", "app.js"));
      const Component = require(_resolve(this.cwd,"_gingerjs","build","app",...props.location.path.split("/"),"index.js"));
      const StaticRouter = require(_resolve(
        "./",
        "_gingerjs",
        "build",
        "app",
        "StaticRouterWrapper.js"
      ));
      const { location } = props;
      const ReactElement = _createElement(Component.default, {
        children: null,
        location,
        ...props,
      });
      const StaticRouterWrapper = _createElement(StaticRouter.default, {
        children: ReactElement,
        url: props.location.path,
      });
      const componentHTML =
          renderToPipeableStream(ReactElement);
      
      // Create an instance of the logging writable stream
      const loggingWritableStream = new LoggingWritableStream();
      const loggingTransformStream = new LoggingTransformStream();
      componentHTML.pipe(loggingTransformStream).pipe(loggingWritableStream);
      // After the stream has ended, the concatenated string can be accessed
      loggingWritableStream.on("finish", () => {
        resolve(loggingWritableStream.renderString())
      });
    })
  }

  createElement(path, props) {
    const componentFile = require(path);
    const Component = componentFile.default; // Import the individual component
    const reactElem = _createElement(Component, {
      ...props,
    });
    return reactElem;
  }
}


export default SSR
