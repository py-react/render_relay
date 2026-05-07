import React from 'react';

export const Layout = ({ children }) => (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-orange-500/30">
        <nav className="border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
                <a href="/" className="text-xl font-bold bg-gradient-to-r from-orange-400 to-rose-400 bg-clip-text text-transparent">
                    Insights & Engineering
                </a>
                <div className="flex gap-8 text-sm font-medium opacity-70">
                    <a href="/" className="hover:opacity-100 transition-opacity">Articles</a>
                    <a href="/about" className="hover:opacity-100 transition-opacity">About</a>
                </div>
            </div>
        </nav>
        <main className="max-w-5xl mx-auto px-6 py-12">
            {children}
        </main>
        <footer className="border-t border-zinc-900 py-12 mt-20">
            <div className="max-w-5xl mx-auto px-6 flex justify-between items-center text-sm opacity-50">
                <p>© 2024 RenderRelay System. All rights reserved.</p>
                <div className="flex gap-6">
                    <a href="#">Twitter</a>
                    <a href="#">GitHub</a>
                </div>
            </div>
        </footer>
    </div>
);

export const PostCard = ({ post }) => (
    <article className="group relative bg-zinc-900/40 border border-zinc-800/50 rounded-2xl p-6 hover:bg-zinc-900/60 transition-all hover:scale-[1.01]">
        <div className="flex justify-between items-start mb-4">
            <time className="text-xs opacity-40 font-mono italic">
                {new Date(post.published_at).toLocaleDateString()}
            </time>
            <div className="flex gap-2">
                {post.tags.map(tag => (
                    <span key={tag.id} className="text-[10px] uppercase tracking-widest bg-orange-500/10 text-orange-400 px-2 py-1 rounded">
                        {tag.name}
                    </span>
                ))}
            </div>
        </div>
        <h2 className="text-2xl font-bold mb-3 group-hover:text-orange-400 transition-colors">
            <a href={`/posts/${post.slug}`}>{post.title}</a>
        </h2>
        <p className="text-zinc-400 line-clamp-2 text-sm leading-relaxed mb-6">
            {post.excerpt}
        </p>
        <div className="flex items-center gap-3">
            <img src={post.author.avatar} className="w-6 h-6 rounded-full bg-zinc-800" alt="" />
            <span className="text-xs font-medium opacity-60">{post.author.name}</span>
        </div>
    </article>
);
