import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

const CreatePost = () => {
    const [title, setTitle] = useState('');
    const [body, setBody] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await client.post('/posts', { title, body });
            navigate('/');
        } catch (error: any) {
            alert(error.response?.data?.message || 'Failed to create post');
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
            <div className="w-full max-w-lg rounded bg-white p-6 shadow-md">
                <h1 className="mb-4 text-center text-2xl font-bold">Create New Post</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="mb-1 block text-sm font-medium text-gray-700">Title</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full rounded border p-2 focus:border-blue-500 focus:outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="mb-1 block text-sm font-medium text-gray-700">Content</label>
                        <textarea
                            value={body}
                            onChange={(e) => setBody(e.target.value)}
                            className="h-32 w-full rounded border p-2 focus:border-blue-500 focus:outline-none"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full rounded bg-gradient-to-r from-indigo-600 to-purple-600 py-2 font-bold text-white hover:opacity-90 transition transform hover:scale-[1.02]"
                    >
                        Publish Post
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate('/')}
                        className="w-full rounded border border-gray-300 bg-white py-2 text-gray-700 hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreatePost;
