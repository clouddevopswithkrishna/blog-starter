import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const { data } = await client.post('/auth/login', { email, password });
            login(data.token);
            navigate('/');
        } catch (error: any) {
            alert(error.response?.data?.message || 'Login failed: ' + error.message);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100">
            <div className="w-full max-w-sm rounded bg-white p-6 shadow-md">
                <h1 className="mb-4 text-center text-2xl font-bold">Login</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full rounded border p-2"
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full rounded border p-2"
                    />
                    <button
                        type="submit"
                        className="w-full rounded bg-gradient-to-r from-indigo-600 to-purple-600 py-2 font-bold text-white hover:opacity-90 transition transform hover:scale-[1.02]"
                    >
                        Login
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
