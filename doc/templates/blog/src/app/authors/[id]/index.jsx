import React from 'react';
import { PostCard } from '../../../components/BlogUI';

export default function AuthorProfile({ author, posts, total, page }) {
    if (!author) return <div className="text-center py-20">Author not found</div>;

    return (
        <div className="space-y-12">
            <header className="flex flex-col items-center text-center space-y-6 max-w-2xl mx-auto">
                <img
                    src={author.avatar}
                    className="w-24 h-24 rounded-full border-2 border-orange-500/20 p-1"
                    alt={author.name}
                />
                <div className="space-y-2">
                    <h1 className="text-4xl font-bold tracking-tight">{author.name}</h1>
                    <p className="text-zinc-400 leading-relaxed">{author.bio}</p>
                </div>
            </header>

            <div className="pt-12 border-t border-zinc-900">
                <div className="flex justify-between items-baseline mb-8">
                    <h2 className="text-xl font-semibold">Published Articles</h2>
                    <span className="text-xs opacity-40 font-mono">{total} posts found</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {posts.map(post => (
                        <PostCard key={post.id} post={post} />
                    ))}
                </div>

                {posts.length === 0 && (
                    <div className="text-center py-20 bg-zinc-900/20 rounded-2xl border border-zinc-800/50">
                        <p className="text-zinc-500 text-sm">No articles published yet.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
