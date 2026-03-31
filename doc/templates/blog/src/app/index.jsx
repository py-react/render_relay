import React from 'react';
import { Layout, PostCard } from '../components/BlogUI';

export default function BlogHome({ posts, total, page, tag }) {
    return (
        <>
            <header className="mb-16">
                <h1 className="text-5xl font-extrabold tracking-tight mb-4">
                    Insights & Engineering
                </h1>
                <p className="text-lg text-zinc-400 max-w-2xl leading-relaxed">
                    Deep dives into full-stack architecture, high-voltage rendering, and the future of RenderRelay development.
                </p>
            </header>

            {tag && (
                <div className="mb-8 flex items-center gap-3 text-sm">
                    <span className="opacity-50 font-medium">Filtering by</span>
                    <span className="bg-orange-500/20 text-orange-400 px-3 py-1 rounded-full border border-orange-500/20">
                        {tag}
                    </span>
                    <a href="/" className="text-zinc-500 hover:text-zinc-300 transition-colors underline underline-offset-4">clear</a>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {posts.map(post => (
                    <PostCard key={post.id} post={post} />
                ))}
            </div>

            {posts.length === 0 && (
                <div className="py-20 text-center border border-dashed border-zinc-800 rounded-3xl opacity-40">
                    No articles found for this criteria.
                </div>
            )}

            <div className="mt-20 flex items-center justify-between border-t border-zinc-900 pt-8">
                <button disabled={page <= 1} className="text-sm font-medium opacity-50 hover:opacity-100 disabled:opacity-20 transition-opacity">
                    ← Newer
                </button>
                <span className="text-xs font-mono opacity-30">Page {page} of {Math.ceil(total / 10)}</span>
                <button disabled={posts.length < 10} className="text-sm font-medium opacity-50 hover:opacity-100 disabled:opacity-20 transition-opacity">
                    Older →
                </button>
            </div>
        </>
    );
}
