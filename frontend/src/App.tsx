import { Routes, Route, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import CreatePost from './pages/CreatePost';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';

const NavBar = () => {
    const { user, logout } = useAuth();
    return (
        <nav className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 font-semibold text-white shadow-lg">
            <div className="container mx-auto flex justify-between items-center">
                <Link to="/" className="text-2xl font-bold tracking-tight hover:text-indigo-100">Blog</Link>
                <div>
                    {user ? (
                        <div className="flex items-center space-x-4">
                            <span>Hello, {user.name || 'User'}</span>
                            <Link to="/create-post" className="rounded bg-white/20 px-4 py-2 hover:bg-white/30 transition">Create Post</Link>
                            <button onClick={logout} className="text-indigo-200 hover:text-white">Logout</button>
                        </div>
                    ) : (
                        <div className="space-x-4">
                            <Link to="/login" className="hover:text-indigo-200 transition">Login</Link>
                            <Link to="/register" className="rounded bg-white px-4 py-2 text-indigo-600 hover:bg-indigo-50 transition">Register</Link>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

const App = () => {
    return (
        <AuthProvider>
            <div className="min-h-screen bg-gray-50">
                <NavBar />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/create-post" element={<CreatePost />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                </Routes>
            </div>
        </AuthProvider>
    );
};

export default App;
