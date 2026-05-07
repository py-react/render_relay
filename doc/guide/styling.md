# Styling

Brahma provides multiple options for styling your React components, giving you the flexibility to choose the tool that best fits your workflow.

## Tailwind CSS

Tailwind CSS is the recommended way to style Brahma applications. It is pre-configured if you selected it during `create-app`.

Simply use Tailwind's utility classes in your JSX:

```jsx
function Button() {
  return (
    <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      Click Me
    </button>
  );
}
```

## CSS Modules

For component-level styles, you can use CSS Modules. Create a file ending in `.module.css`.

**src/components/MyComponent.module.css**
```css
.container {
  padding: 20px;
  background-color: #f0f0f0;
}
```

**src/components/MyComponent.jsx**
```jsx
import styles from './MyComponent.module.css';

function MyComponent() {
  return <div className={styles.container}>Hello World</div>;
}
```

## Styled Components

To use `styled-components` with SSR support, you must configure the `getAppContext` hook in your root `layout.jsx`.

```jsx
import { ServerStyleSheet } from 'styled-components';

export const getAppContext = async (ctx) => {
  const sheet = new ServerStyleSheet();
  ctx.renderApp = () => ({
    enhanceApp: (App) => App,
    getStyles: (App) => sheet.collectStyles(App),
    styles: () => sheet.getStyleTags(),
    finally: () => {
      sheet.seal()
    }
  })
  return ctx
}
```
