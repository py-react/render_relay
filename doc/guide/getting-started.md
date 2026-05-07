# Getting Started

Get up and running with Brahma in minutes.

## Installation

### 1. Create a Virtual Environment
We recommend using a virtual environment to manage your Python dependencies.

```bash
virtualenv env
source env/bin/activate
```

### 2. Install Brahma
Install the Brahma CLI using `pip`:

```bash
pip install git+https://github.com/py-react/render_relay.git
```

## Creating Your First App

Once installed, use the CLI to scaffold a new project:

```bash
render_relay create-app
```

Follow the prompts to configure your project (Tailwind CSS, TypeScript, etc.).

## Running the Development Server

Start the development server with hot-reloading:

```bash
render_relay runserver dev
```

Your application will be available at `http://localhost:5001`.
