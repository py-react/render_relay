import { defineConfig, mergeConfig } from "vite";
import fs from "fs";
import path from "path";
import svgr from "vite-plugin-svgr";
import { viteStaticCopy } from "vite-plugin-static-copy";
import tailwindcss from "tailwindcss";
import autoprefixer from "autoprefixer";
import { existsSync } from "fs";
import { resolve } from "path";
import { readFile, writeFile, readdir } from 'node:fs/promises';
import tsconfigPaths from 'vite-tsconfig-paths'
import react from "@vitejs/plugin-react";
function vitePluginInjectLayout() {
  return {
    name: 'vite-plugin-inject-layout',
    async writeBundle(options, bundle) {
      const layoutPath = path.join(process.cwd(), "public", "templates", MAIN_HTML);
      const outDir = path.join(process.cwd(), "_gingerjs", "build","templates");
      const indexPath = resolve(outDir, 'layout.html'); // Output HTML file
      const jsFileDir = path.join(process.cwd(), "_gingerjs", "build","static","js")
      const cssFileDir = path.join(process.cwd(), "_gingerjs", "build","static","css")
      try {
        const layoutContent = await readFile(layoutPath, 'utf-8');
        let scriptTags = '';

        async function findCssFiles(directory) {
          const files = await readdir(directory, { withFileTypes: true });
          for (const file of files) {
            const fullPath = path.join(directory, file.name);
            if (file.isDirectory()) {
              await findCssFiles(fullPath);
            } else if (file.name.endsWith('.css')) {
              const publicPath = fullPath.replace(cssFileDir, '/static/css');
              scriptTags += `<link rel="stylesheet" href="${publicPath}">\n`;
            }
          }
        }
        // Function to recursively find .js files in the output directory
        async function findJsFiles(directory) {
          const files = await readdir(directory, { withFileTypes: true });
          for (const file of files) {
            const fullPath = path.join(directory, file.name);
            if (file.isDirectory()) {
              await findJsFiles(fullPath);
            } else if (file.name.endsWith('.js')) {
              const publicPath = fullPath.replace(jsFileDir, '/static/js');
              scriptTags += `<script defer type="module" src="${publicPath}"></script>\n`;
            }
          }
        }
        

        // Start the search for JS files in the root of the output directory
        await findJsFiles(jsFileDir);
        await findCssFiles(cssFileDir);

        const headTagIndex = layoutContent.lastIndexOf('</head>');
        if (headTagIndex !== -1) {
          const updatedContent =
            layoutContent.slice(0, headTagIndex) +
            scriptTags +
            layoutContent.slice(headTagIndex);

          await writeFile(indexPath, updatedContent);
          console.log('Vite Plugin: Script tags injected into layout.html');
        } else {
          console.error('Vite Plugin: </head> tag not found in layout.html');
        }
      } catch (error) {
        console.error('Vite Plugin Error:', error);
      }
    },
  };
}

const vendorChunks = {
  mui: [/@mui/, /@emotion/, /mui/],
  styles: [
    /styled-components/,
    /radix-ui/,
    /css-/,
    /lucide-react/,
    /floating-ui/,
  ],
  react: [/react/, /react-dom/, /react-icons/, /react-router/],
  redux: [
    /redux/,
    /react-redux/,
    /@reduxjs/,
    /redux-sentry-middleware/,
    /addon-redux/,
    /reselect/,
  ],
  phone: [
    /react-phone-number-input/,
    /libphonenumber-js/,
    /country-flag-icons/,
  ],
  monitoring: [/@segment/, /@datadog/],
  experimentation: [/@optimizely/, /opticks/],
  intl: [/@formatjs/, /intl-formatmessage/],
  aws: [/@aws-amplify/, /aws-amplify/, /@aws-sdk/, /@aws-crypto/],
};

// Load environment variables
const STATIC_SITE = process.env.STATIC_SITE === "True";
const MODE = true ? "development" : "production";
const MAIN_HTML = STATIC_SITE ? "index.html" : "layout.html";
const TAILWIND = process.env.TAILWIND === "True";
const staticPath = "/static/";

async function getOverrides() {
  const overridePath = resolve(process.cwd(), "ginger_conf.cjs");
  if (existsSync(overridePath)) {
    const overrides = await import(overridePath);
    return overrides.default || overrides;
  }
  return {};
}

async function buildConfig() {
  const overrides = await getOverrides();

  // Determine entry points
  const entry = {
      main:path.resolve(process.cwd(), "_gingerjs", "__build__", "main.jsx"),
      global:path.resolve(process.cwd(), "src", "global.css")
  };

  if (!fs.existsSync(path.resolve(process.cwd(), "src", "global.css"))) {
    delete entry.global;
  }

  // Define plugins
  const plugins = [
    react({
      jsxRuntime: 'classic', // or 'classic'
    }),
    tsconfigPaths(),
    svgr(),
    viteStaticCopy({
      targets: [
        {
          src: path.join("public", "static", "**/*"),
          dest: "./assets/",
        },
      ],
    }),
    vitePluginInjectLayout(),
  ];
  // Add Tailwind CSS if enabled
  if (TAILWIND) {
    plugins.push({
      name: "tailwindcss",
      config() {
        return {
          css: {
            postcss: {
              plugins: [tailwindcss(), autoprefixer()],
            },
          },
        };
      },
    });
  }

  // Base Vite configuration
  const baseConfig = defineConfig({
    root: process.cwd(),
    base: staticPath,
    mode: MODE,
    build: {
      outDir: path.resolve(process.cwd(), "_gingerjs", "build", "static"),
      copyPublicDir: false, 
      sourcemap:false,
      rollupOptions: {
        input: entry,
        external:[],
        preserveEntrySignatures:true,
        output: {
          entryFileNames:
            MODE === "development" ? "js/[name].js" : "js/[name].[hash].js",
          chunkFileNames:
            MODE === "development" ? "js/[name].js" : "js/[name].[hash].js",
          assetFileNames:
            MODE === "development"
              ? "css/[name].[ext]"
              : "css/[name].[hash].[ext]",
          manualChunks: (id) => {
            // // Match against vendor chunk patterns
            // for (const [name, patterns] of Object.entries(vendorChunks)) {
            //     if (patterns.some((pattern) => pattern.test(id))) {
            //     return name;
            //     }
            // }
            // Default vendor chunk for node_modules
            if (id.includes("node_modules")) {
                return "vendor";
            }
          },
        },
      },
    },
    
    plugins,
  });

  return mergeConfig(baseConfig, overrides.vite || {});
}

export default buildConfig;
