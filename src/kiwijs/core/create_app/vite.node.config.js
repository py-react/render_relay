import { defineConfig, mergeConfig } from "vite";
import fs from "fs";
import path from "path";
import react from "@vitejs/plugin-react";
import tailwindcss from "tailwindcss";
import autoprefixer from "autoprefixer";
import { existsSync } from "fs";
import { resolve } from "path";
import tsconfigPaths from 'vite-tsconfig-paths'
import { viteCommonjs } from '@originjs/vite-plugin-commonjs'


// Load environment variables
const MODE = true ? "development" : "production";
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
  const entry = [
    path.resolve(process.cwd(), "_gingerjs", "__build__", "main.jsx"),
    path.resolve(
      process.cwd(),
      "_gingerjs",
      "__build__",
      "StaticRouterWrapper.jsx"
    ),
    path.resolve(process.cwd(), "_gingerjs", "__build__", "DefaultLoader.jsx"),
    ...(process.env.DEBUG === "True"
      ? [path.resolve(process.cwd(), "_gingerjs", "__build__", "Error.jsx")]
      : []),

    path.resolve(
      process.cwd(),
      "_gingerjs",
      "__build__",
      "GenericNotFound.jsx"
    ),
    path.resolve(
      process.cwd(),
      "_gingerjs",
      "__build__",
      "LayoutPropsProvider.jsx"
    ),
    path.resolve(process.cwd(), "_gingerjs", "__build__", "PropsProvider.jsx"),
  ];

  // Define plugins
  const plugins = [
    react({
      jsxRuntime: 'classic', // or 'classic'
    }),
    tsconfigPaths(),
    viteCommonjs()
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
      // emptyOutDir:false,
      outDir: path.resolve(process.cwd(), "_gingerjs", "build"),
      copyPublicDir: false, 
      ssr: true,
      rollupOptions: {
        input: entry,
        // external:[/node_modules/],
        preserveEntrySignatures:true,
        output: {
          preserveModulesRoot:"src",
          preserveModules: true,
          entryFileNames:
            MODE === "development" ? "[name].js" : "[name].[hash].js",
          chunkFileNames:
            MODE === "development" ? "[name].js" : "[name].[hash].js",
          assetFileNames:
            MODE === "development"
              ? "[name].[ext]"
              : "[name].[hash].[ext]",
        },
      },
    },
    plugins,
  });

  return mergeConfig(baseConfig, overrides.vite_node || {});
}

export default buildConfig;
