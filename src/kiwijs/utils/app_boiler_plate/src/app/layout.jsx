import React from 'react'
import { Outlet } from 'react-router-dom'
import { ThemeProvider } from "src/libs/theme-provider"

function Layout() {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <div className="h-screen w-screen overflow-hidden bg-[#080808] text-white">
        <Outlet />
      </div>
    </ThemeProvider>
  );
}

export default Layout