import React, { useState } from "react";
import {
  BookOpen,
  Zap,
  Globe,
  Code2,
  ArrowRight,
  Copy,
  Check,
  Terminal,
  Layers,
  ExternalLink,
} from "lucide-react";

// ─── Tiny inline SVG kiwi logo mark ─────────────────────────────────────────
function KiwiMark({ size = 32 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="KiwiJS logo"
    >
      {/* Outer circle glow ring */}
      <circle cx="20" cy="20" r="19" stroke="#84cc16" strokeWidth="1.5" strokeOpacity="0.4" />
      {/* Main circle */}
      <circle cx="20" cy="20" r="15" fill="url(#kiwiGrad)" />
      {/* Kiwi slice lines */}
      <line x1="20" y1="5" x2="20" y2="35" stroke="#ffffff" strokeWidth="1.2" strokeOpacity="0.3" />
      <line x1="5" y1="20" x2="35" y2="20" stroke="#ffffff" strokeWidth="1.2" strokeOpacity="0.3" />
      <line x1="9.4" y1="9.4" x2="30.6" y2="30.6" stroke="#ffffff" strokeWidth="1.2" strokeOpacity="0.2" />
      <line x1="30.6" y1="9.4" x2="9.4" y2="30.6" stroke="#ffffff" strokeWidth="1.2" strokeOpacity="0.2" />
      {/* Centre seed */}
      <circle cx="20" cy="20" r="3" fill="#ffffff" fillOpacity="0.85" />
      <defs>
        <radialGradient id="kiwiGrad" cx="35%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#a3e635" />
          <stop offset="100%" stopColor="#4d7c0f" />
        </radialGradient>
      </defs>
    </svg>
  );
}

// ─── Copy-to-clipboard button ────────────────────────────────────────────────
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback – silent
    }
  };

  return (
    <button
      onClick={handleCopy}
      aria-label="Copy command"
      className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-zinc-400 transition-all duration-200 hover:bg-white/10 hover:text-white active:scale-95"
    >
      {copied ? (
        <>
          <Check size={13} className="text-lime-400" />
          <span className="text-lime-400">Copied</span>
        </>
      ) : (
        <>
          <Copy size={13} />
          Copy
        </>
      )}
    </button>
  );
}

// ─── Quick-action card ───────────────────────────────────────────────────────
function ActionCard({ icon: Icon, label, description, href, accent = false }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={`group relative flex flex-col gap-2.5 overflow-hidden rounded-xl border p-5 transition-all duration-300
        ${
          accent
            ? "border-lime-500/30 bg-lime-950/20 hover:border-lime-400/60 hover:bg-lime-950/40 hover:shadow-[0_0_24px_-4px_rgba(132,204,22,0.3)]"
            : "border-white/[0.07] bg-white/[0.03] hover:border-white/[0.15] hover:bg-white/[0.07]"
        }
      `}
    >
      {/* subtle top shimmer on hover */}
      <span className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      <div className="flex items-center justify-between">
        <span
          className={`flex h-8 w-8 items-center justify-center rounded-lg ${
            accent ? "bg-lime-500/20 text-lime-400" : "bg-white/[0.06] text-zinc-400"
          } transition-colors duration-300 group-hover:text-white`}
        >
          <Icon size={15} />
        </span>
        <ExternalLink
          size={13}
          className="text-zinc-600 opacity-0 transition-all duration-200 group-hover:opacity-100 group-hover:text-zinc-400"
        />
      </div>

      <div>
        <p className={`text-sm font-semibold ${accent ? "text-lime-300" : "text-zinc-200"}`}>
          {label}
        </p>
        <p className="mt-0.5 text-xs text-zinc-500 leading-relaxed">{description}</p>
      </div>

      <ArrowRight
        size={13}
        className="mt-auto text-zinc-600 transition-all duration-200 group-hover:translate-x-1 group-hover:text-zinc-400"
      />
    </a>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────
export default function Home() {
  const [activeTab, setActiveTab] = useState("start");

  const tabs = [
    {
      id: "start",
      label: "Get started",
      command: "# Edit your first route\nsrc/app/index.jsx",
      lang: "bash",
    },
    {
      id: "dev",
      label: "Dev server",
      command: "npm run dev\n\n# ✓ Ready on http://localhost:5173",
      lang: "bash",
    },
    {
      id: "api",
      label: "API route",
      command:
        '# src/app/api/hello/index.py\nfrom kiwijs import api\n\n@api.get("/api/hello")\ndef handler():\n    return {"message": "Hello from KiwiJS"}',
      lang: "python",
    },
  ];

  const activeSnippet = tabs.find((t) => t.id === activeTab);

  return (
    <main className="relative flex h-screen w-screen flex-col items-center justify-center overflow-hidden bg-[#080808] font-sans text-white">

      {/* ── Ambient background glows ─────────────────────────────────────── */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        {/* Top-centre lime glow */}
        <div className="absolute -top-24 left-1/2 h-[480px] w-[680px] -translate-x-1/2 rounded-full bg-lime-500/10 blur-[120px]" />
        {/* Bottom-right violet accent */}
        <div className="absolute bottom-0 right-0 h-[300px] w-[400px] translate-x-1/4 translate-y-1/4 rounded-full bg-violet-600/8 blur-[100px]" />
        {/* Bottom-left blue accent */}
        <div className="absolute bottom-0 left-0 h-[260px] w-[340px] -translate-x-1/4 translate-y-1/4 rounded-full bg-sky-500/8 blur-[90px]" />

        {/* Fine dot grid */}
        <div
          className="absolute inset-0 opacity-[0.18]"
          style={{
            backgroundImage:
              "radial-gradient(circle, rgba(255,255,255,0.35) 1px, transparent 1px)",
            backgroundSize: "28px 28px",
          }}
        />

        {/* Vignette overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#080808]/60 via-transparent to-[#080808]/80" />
      </div>

      {/* ── Top nav bar ──────────────────────────────────────────────────── */}
      <nav className="absolute top-0 left-0 right-0 flex items-center justify-between px-6 py-4 sm:px-10">
        <div className="flex items-center gap-2.5">
          <KiwiMark size={28} />
          <span className="text-sm font-semibold tracking-tight text-white/90">KiwiJS</span>
          <span className="ml-1 rounded-full border border-lime-500/30 bg-lime-500/10 px-2 py-0.5 text-[10px] font-medium text-lime-400 uppercase tracking-wider">
            v1.0
          </span>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="https://github.com/py-react/render_relay"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-1.5 text-xs text-zinc-400 transition-all duration-200 hover:border-white/20 hover:text-white"
          >
            <Code2 size={12} />
            GitHub
          </a>
          <a
            href="https://github.com/py-react/render_relay?tab=readme-ov-file"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg bg-lime-500 px-3 py-1.5 text-xs font-semibold text-black transition-all duration-200 hover:bg-lime-400 hover:shadow-[0_0_16px_rgba(132,204,22,0.4)] active:scale-95"
          >
            Docs
            <ArrowRight size={12} />
          </a>
        </div>
      </nav>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="relative z-10 flex w-full max-w-5xl flex-col items-center gap-10 px-4 sm:px-6">

        {/* Status badge */}
        <div className="flex items-center gap-2 rounded-full border border-lime-500/20 bg-lime-500/[0.07] px-3.5 py-1.5">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-lime-400 opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-lime-400" />
          </span>
          <span className="text-xs text-lime-400/90 font-medium">Dev server running</span>
        </div>

        {/* Hero text */}
        <div className="flex flex-col items-center gap-4 text-center">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            <span className="bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent">
              Build faster with
            </span>
            <br />
            <span className="bg-gradient-to-r from-lime-300 via-lime-400 to-green-400 bg-clip-text text-transparent">
              KiwiJS
            </span>
          </h1>
          <p className="max-w-md text-sm text-zinc-400 leading-relaxed sm:text-base">
            A modern fullstack framework for building production-ready applications with less setup.
          </p>
        </div>

        {/* ── Code snippet card ─────────────────────────────────────────── */}
        <div className="w-full max-w-xl overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.03] shadow-[0_0_60px_-10px_rgba(0,0,0,0.8)] backdrop-blur-sm">
          {/* Tab bar */}
          <div className="flex items-center gap-1 border-b border-white/[0.06] bg-white/[0.02] px-4 py-2.5">
            <div className="flex gap-1.5 mr-3">
              <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-lime-500/60" />
            </div>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-all duration-150 ${
                  activeTab === tab.id
                    ? "bg-white/[0.1] text-white"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
            <div className="ml-auto">
              <CopyButton text={activeSnippet?.command ?? ""} />
            </div>
          </div>

          {/* Code body */}
          <div className="px-5 py-4 min-h-[96px]">
            <div className="flex items-start gap-3">
              <Terminal size={14} className="mt-0.5 shrink-0 text-lime-500/70" />
              <pre className="flex-1 overflow-x-auto font-mono text-xs leading-relaxed text-zinc-300 whitespace-pre">
                {activeSnippet?.command}
              </pre>
            </div>
          </div>
        </div>

        {/* ── Quick-action cards ────────────────────────────────────────── */}
        <div className="grid w-full max-w-3xl grid-cols-2 gap-3 sm:grid-cols-4">
          <ActionCard
            icon={BookOpen}
            label="Docs"
            description="Full API reference & guides"
            href="https://github.com/py-react/render_relay?tab=readme-ov-file"
            accent
          />
          <ActionCard
            icon={Layers}
            label="Routing"
            description="File-system based routing"
            href="https://github.com/py-react/render_relay?tab=readme-ov-file#layouts"
          />
          <ActionCard
            icon={Zap}
            label="API Routes"
            description="Python-powered endpoints"
            href="https://github.com/py-react/render_relay?tab=readme-ov-file#getting-started"
          />
          <ActionCard
            icon={Globe}
            label="Deploy"
            description="Production-ready builds"
            href="https://github.com/py-react/render_relay?tab=readme-ov-file"
          />
        </div>
      </div>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-6 py-4 sm:px-10">
        <p className="text-[11px] text-zinc-600">
          KiwiJS · Python + React Fullstack Framework
        </p>
        <p className="font-mono text-[11px] text-zinc-700">
          src/app/index.jsx
        </p>
      </footer>
    </main>
  );
}
