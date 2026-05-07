import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Brahma",
  description: "Full-Stack Development Experience with Python and React",
  themeConfig: {
    logo: {
      light: '/static/brahma_logo_light.svg',
      dark: '/static/brahma_logo_dark.svg'
    },
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Templates', link: '/templates/' },
      { text: 'Guide', link: '/guide/what-is-brahma' }
    ],
    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'What is Brahma?', link: '/guide/what-is-brahma' },
          { text: 'Getting Started', link: '/guide/getting-started' },
          { text: 'CLI Reference', link: '/guide/cli-reference' }
        ]
      },
      {
        text: 'Core Concepts',
        items: [
          { text: 'Project Structure', link: '/guide/project-structure' },
          { text: 'Routing', link: '/guide/routing' },
          { text: 'Rendering', link: '/guide/rendering' },
          { text: 'Data Fetching', link: '/guide/data-fetching' },
          { text: 'State Management', link: '/guide/state-management' },
          { text: 'Architecture', link: '/guide/architecture' }
        ]
      },
      {
        text: 'Building with Brahma',
        items: [
          { text: 'WebSockets', link: '/guide/websockets' },
          { text: 'Middleware', link: '/guide/middleware' },
          { text: 'Styling', link: '/guide/styling' },
          { text: 'Meta Data', link: '/guide/metadata' }
        ]
      },
      {
        text: 'Advanced',
        items: [
          { text: 'Extending App', link: '/guide/extending' },
          { text: 'Configuration', link: '/guide/configuration' },
          { text: 'Error Handling', link: '/guide/error-handling' },
          { text: 'Static Site (SSG)', link: '/guide/ssg' }
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/py-react/render_relay' }
    ],
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026-present Brahma Team'
    }
  }
})
