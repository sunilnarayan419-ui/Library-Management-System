const { useState, useEffect, useContext, createContext } = React;

// --- 0. Context & Utils ---
const API_BASE = '/api';
const AuthContext = createContext(null);
const ThemeContext = createContext(null);

const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within AuthProvider");
    return context;
};

const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) throw new Error("useTheme must be used within ThemeProvider");
    return context;
};

// --- 1. Utilities & Hooks ---
const useBooks = () => {
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(null);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const refresh = () => setRefreshTrigger(p => p + 1);

    useEffect(() => {
        fetch(`${API_BASE}/books`)
            .then(res => res.json())
            .then(data => {
                setBooks(data);
                setLoading(false);
            })
            .catch(err => console.error(err));

        fetch(`${API_BASE}/stats`)
            .then(res => res.json())
            .then(data => setStats(data))
            .catch(err => console.error(err));
    }, [refreshTrigger]);

    return { books, stats, loading, refresh };
};

// --- 2. UI Components ---

const Icon = ({ name, size = 24, className = "" }) => {
    useEffect(() => {
        if (window.lucide) window.lucide.createIcons();
    });
    return <i data-lucide={name} style={{ width: size, height: size }} className={`inline-block ${className}`}></i>;
};

const GlassCard = ({ children, className = "", hover = true }) => (
    <div className={`glass-card rounded-2xl p-6 text-slate-900 dark:text-white ${className} ${hover ? 'transition-all duration-500 hover:bg-white/40 dark:hover:bg-white/5 hover:scale-[1.01] hover:shadow-xl dark:hover:shadow-indigo-500/10' : ''} border border-slate-200 dark:border-white/5`}>
        {children}
    </div>
);

const Button = ({ children, onClick, variant = 'primary', className = "", disabled = false, type = "button" }) => {
    const base = "px-6 py-3 rounded-xl font-semibold transition-all duration-300 transform active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed";
    const variants = {
        primary: "bg-gradient-to-r from-primary to-indigo-600 hover:to-indigo-500 shadow-lg shadow-primary/30 text-white",
        accent: "bg-gradient-to-r from-accent to-cyan-400 hover:to-cyan-300 shadow-lg shadow-accent/30 text-slate-900 border border-t-white/20",
        danger: "bg-gradient-to-r from-red-500 to-rose-600 hover:to-rose-500 shadow-lg shadow-red-500/30 text-white",
        ghost: "hover:bg-black/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white border border-transparent hover:border-black/5 dark:hover:border-white/10"
    };
    return (
        <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${variants[variant]} ${className}`}>
            {children}
        </button>
    );
};

const Input = ({ label, type = "text", value, onChange, placeholder, required = false }) => (
    <div className="flex flex-col gap-2 mb-5">
        <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex justify-between">
            {label} {required && <span className="text-red-400">*</span>}
        </label>
        <input
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            required={required}
            className="w-full bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-xl px-5 py-3 text-slate-900 dark:text-white outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all placeholder:text-slate-400 focus:bg-white dark:focus:bg-slate-800/80"
        />
    </div>
);

const Modal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 dark:bg-black/80 backdrop-blur-md p-4 animate-fade-in">
            <div className="glass-card w-full max-w-lg rounded-3xl relative animate-scale-up border border-white/20 dark:border-white/10 shadow-2xl overflow-hidden bg-white/80 dark:bg-slate-900/50">
                <div className="flex justify-between items-center p-6 border-b border-black/5 dark:border-white/5 bg-black/5 dark:bg-white/5">
                    <h2 className="text-xl font-bold font-heading text-slate-900 dark:text-white">{title}</h2>
                    <button onClick={onClose} className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-black/10 dark:hover:bg-white/10 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                        <Icon name="x" size={18} />
                    </button>
                </div>
                <div className="p-6">
                    {children}
                </div>
            </div>
        </div>
    );
};

const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();
    return (
        <button onClick={toggleTheme} className="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-yellow-400 hover:scale-110 transition-transform shadow-inner">
            <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={20} />
        </button>
    );
};

// --- 3. Login Flow ---

const Login = () => {
    const { login } = useAuth();
    const [role, setRole] = useState('student'); // 'student' | 'admin' | 'librarian'
    const [formData, setFormData] = useState({ email: '', mobile: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role,
                    ...formData
                })
            });
            const data = await res.json();

            if (data.success) {
                login(data.user);
            } else {
                setError(data.message || 'Login failed');
            }
        } catch (err) {
            setError('Connection error. Is server running?');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-50 dark:bg-transparent">
            {/* Background Effects */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(99,102,241,0.1),transparent_70%)]"></div>
                <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/20 rounded-full blur-[80px] animate-pulse-slow"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[100px] animate-pulse-slow text-glow" style={{ animationDelay: '1s' }}></div>
            </div>

            <div className="absolute top-6 right-6 z-20">
                <ThemeToggle />
            </div>

            <div className="w-full max-w-md relative z-10 perspective-1000">
                <GlassCard className="border-t border-l border-white/20 dark:border-white/10 shadow-2xl backdrop-blur-3xl" hover={false}>
                    <div className="text-center mb-8">
                        <div className="w-16 h-16 bg-gradient-to-tr from-primary to-accent rounded-2xl mx-auto flex items-center justify-center shadow-lg shadow-primary/20 mb-4 animate-float">
                            <Icon name="library" className="text-white" size={32} />
                        </div>
                        <h1 className="text-3xl font-bold font-heading text-slate-900 dark:text-white mb-2">Welcome Back</h1>
                        <p className="text-slate-500 dark:text-slate-400">Sign in to access the library</p>
                    </div>

                    <div className="flex p-1 bg-slate-200 dark:bg-slate-900/50 rounded-xl mb-8 relative">
                        {['student', 'admin', 'librarian'].map(r => (
                            <button
                                key={r}
                                onClick={() => setRole(r)}
                                className={`flex-1 py-2 rounded-lg text-sm font-semibold capitalize transition-all duration-300 ${role === r ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-lg' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}`}
                            >
                                {r}
                            </button>
                        ))}
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4 animate-fade-in key={role}">
                        {role === 'student' ? (
                            <>
                                <Input
                                    label="Email Address"
                                    placeholder="student@university.edu"
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    required
                                />
                                <Input
                                    label="Mobile Number"
                                    placeholder="10-digit number"
                                    value={formData.mobile}
                                    onChange={e => setFormData({ ...formData, mobile: e.target.value })}
                                    required
                                />
                            </>
                        ) : (
                            <Input
                                label={`${role.charAt(0).toUpperCase() + role.slice(1)} Password`}
                                type="password"
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={e => setFormData({ ...formData, password: e.target.value })}
                                required
                            />
                        )}

                        {error && (
                            <div className="bg-red-100 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg flex items-center gap-2">
                                <Icon name="alert-circle" size={16} /> {error}
                            </div>
                        )}

                        <Button type="submit" variant="primary" className="w-full mt-6" disabled={loading}>
                            {loading ? 'Authenticating...' : 'Sign In'} <Icon name="arrow-right" size={18} />
                        </Button>
                    </form>
                </GlassCard>

                <div className="text-center mt-6 text-slate-500 dark:text-slate-500 text-sm">
                    Only authorized personnel and students may access.
                </div>
            </div>
        </div>
    );
};

// --- 4. Main App Pages ---

const Sidebar = ({ activeTab, onChangeTab, user, onLogout }) => {
    const items = [
        { id: 'dashboard', label: 'Dashboard', icon: 'layout-dashboard', allowed: ['admin', 'student', 'librarian'] },
        { id: 'books', label: 'Library Books', icon: 'book', allowed: ['admin', 'student', 'librarian'] },
        { id: 'student', label: 'My Profile', icon: 'user', allowed: ['student'] },
        // New History Feature
        { id: 'history', label: 'Issue History', icon: 'history', allowed: ['admin', 'librarian'] },
    ];

    return (
        <aside className="w-20 lg:w-72 h-screen fixed left-0 top-0 bg-white/80 dark:bg-slate-900/50 backdrop-blur-md border-r border-slate-200 dark:border-white/5 flex flex-col z-40 transition-all shadow-2xl">
            <div className="h-24 flex items-center justify-center lg:justify-start lg:px-8 border-b border-slate-200 dark:border-white/5 bg-slate-50/50 dark:bg-white/[0.02]">
                <div className="w-10 h-10 bg-gradient-to-tr from-primary to-accent rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 shrink-0">
                    <Icon name="library" className="text-white" size={20} />
                </div>
                <div className="hidden lg:block ml-4">
                    <span className="block font-bold text-lg tracking-tight leading-none text-slate-900 dark:text-white">LMS <span className="text-accent">AI</span></span>
                    <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase">Version 4.0</span>
                </div>
            </div>

            <nav className="flex-1 py-8 flex flex-col gap-2 px-3">
                {items.filter(i => i.allowed.includes(user.role)).map(item => (
                    <button
                        key={item.id}
                        onClick={() => onChangeTab(item.id)}
                        className={`w-full flex items-center justify-center lg:justify-start lg:px-6 py-4 rounded-2xl transition-all duration-300 group ${activeTab === item.id
                                ? 'bg-gradient-to-r from-primary to-indigo-600 text-white shadow-lg shadow-primary/20 scale-[1.02]'
                                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white'
                            }`}
                    >
                        <Icon name={item.icon} size={22} className={activeTab === item.id ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'} />
                        <span className="hidden lg:block ml-4 font-medium text-sm tracking-wide">{item.label}</span>
                        {activeTab === item.id && <div className="ml-auto hidden lg:block w-1.5 h-1.5 rounded-full bg-white shadow-glow"></div>}
                    </button>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-200 dark:border-white/5 flex flex-col gap-4">
                <div className="flex justify-center lg:justify-start pl-2">
                    <ThemeToggle />
                </div>

                <div className="glass-card bg-slate-100 dark:bg-slate-900/50 rounded-2xl p-4 flex items-center gap-3 hover:bg-white dark:hover:bg-slate-800 transition-colors cursor-pointer group hover:border-slate-300 dark:hover:border-slate-600">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center group-hover:from-primary group-hover:to-accent transition-colors">
                        <span className="font-bold text-slate-700 dark:text-white text-sm">{user.name.charAt(0)}</span>
                    </div>
                    <div className="hidden lg:block overflow-hidden">
                        <p className="text-sm font-bold text-slate-800 dark:text-white truncate">{user.name}</p>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">{user.role}</p>
                    </div>
                </div>

                <button onClick={onLogout} className="w-full py-2 flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 hover:text-red-500 dark:hover:text-red-400 text-xs font-bold uppercase tracking-wider transition-colors">
                    <Icon name="log-out" size={14} /> <span className="hidden lg:inline">Sign Out</span>
                </button>
            </div>
        </aside>
    );
};

const Dashboard = ({ stats, user }) => {
    // ... same as before but safe check
    const cards = [
        { label: 'Total Books', value: stats?.total_books || 0, icon: 'book-open', color: 'from-blue-500 to-indigo-500' },
        { label: 'Issued Books', value: stats?.issued_books || 0, icon: 'layers', color: 'from-orange-500 to-pink-500' },
        { label: 'Available', value: stats?.available_books || 0, icon: 'check-circle', color: 'from-emerald-500 to-teal-500' },
        { label: 'Members', value: stats?.members || 0, icon: 'users', color: 'from-violet-500 to-purple-500' },
    ];

    return (
        <div className="space-y-8 animate-fade-in pl-0 lg:pl-6 max-w-7xl mx-auto">
            <header className="flex justify-between items-end pb-6 border-b border-slate-200 dark:border-white/5">
                <div>
                    <h1 className="text-4xl font-bold font-heading text-slate-900 dark:text-white mb-2 tracking-tight">Dashboard</h1>
                    <p className="text-slate-500 dark:text-slate-400">Overview of library activity and metrics.</p>
                </div>
                <div className="hidden md:block text-right">
                    <p className="text-sm text-slate-500 dark:text-slate-400">Current Date</p>
                    <p className="text-lg font-mono text-slate-800 dark:text-white">{new Date().toLocaleDateString()}</p>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {cards.map((card, idx) => (
                    <GlassCard key={idx} className="relative overflow-hidden group">
                        <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${card.color} opacity-10 rounded-full blur-2xl transform translate-x-10 -translate-y-10 group-hover:opacity-20 transition-all duration-700`}></div>
                        <div className="flex justify-between items-start mb-6">
                            <div className={`p-3 rounded-2xl bg-gradient-to-br ${card.color} shadow-lg shadow-black/20 text-white`}>
                                <Icon name={card.icon} size={24} />
                            </div>
                            <div className="flex items-center text-green-500 dark:text-green-400 text-xs font-bold bg-green-100 dark:bg-green-400/10 px-2 py-1 rounded-full">
                                <Icon name="trending-up" size={12} className="mr-1" /> +2.4%
                            </div>
                        </div>
                        <div className="text-4xl font-bold text-slate-900 dark:text-white mb-1 tracking-tight">{card.value}</div>
                        <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">{card.label}</div>
                    </GlassCard>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Visual Analytics Bar Chart */}
                <GlassCard className="lg:col-span-2 min-h-[400px] flex flex-col relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-100/50 dark:to-slate-900/50 pointer-events-none"></div>
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="font-bold text-lg text-slate-900 dark:text-white">Weekly Traffic</h3>
                        <select className="bg-slate-200 dark:bg-slate-800 text-xs text-slate-700 dark:text-white px-3 py-1 rounded-lg outline-none border border-slate-300 dark:border-slate-700">
                            <option>This Week</option>
                            <option>This Month</option>
                        </select>
                    </div>

                    {/* Visual Mockup of bars */}
                    <div className="flex-1 flex items-end justify-between px-4 gap-2 border-b border-slate-200 dark:border-white/5 pb-2">
                        {[40, 65, 33, 87, 56, 92, 45].map((h, i) => (
                            <div key={i} className="w-full bg-slate-200 dark:bg-slate-800 hover:bg-primary/50 transition-colors rounded-t-lg relative group" style={{ height: `${h}%` }}>
                                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-white text-slate-900 text-xs font-bold px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity shadow-md">
                                    {h}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between mt-4 text-xs text-slate-500 uppercase font-bold tracking-wider">
                        <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                    </div>
                </GlassCard>

                <GlassCard className="min-h-[400px]">
                    <h3 className="font-bold text-lg text-slate-900 dark:text-white mb-6">Recent Activity</h3>
                    <div className="space-y-6">
                        {[1, 2, 3, 4].map(i => (
                            <div key={i} className="flex gap-4 group cursor-default">
                                <div className="relative">
                                    <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center z-10 relative group-hover:border-accent transition-colors">
                                        <Icon name={i % 2 === 0 ? "book-open" : "check"} size={16} className={i % 2 === 0 ? "text-orange-500 dark:text-orange-400" : "text-green-500 dark:text-green-400"} />
                                    </div>
                                    {i !== 4 && <div className="absolute top-10 left-1/2 -translate-x-1/2 w-px h-full bg-slate-200 dark:bg-slate-800 group-hover:bg-slate-300 dark:group-hover:bg-slate-700"></div>}
                                </div>
                                <div className="flex-1 pb-2">
                                    <p className="text-sm font-medium text-slate-800 dark:text-white group-hover:text-accent transition-colors">Practical Research Methods</p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{i % 2 === 0 ? "Borrowed by John Doe" : "Returned by Jane Smith"}</p>
                                    <p className="text-[10px] text-slate-400 dark:text-slate-600 font-mono mt-2">2 HOURS AGO</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </GlassCard>
            </div>
        </div>
    );
};

const BookList = ({ books, refresh, onIssue, onReturn, onDelete, user }) => {
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("All"); // All | Available | Issued
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [newBookTitle, setNewBookTitle] = useState("");
    const [view, setView] = useState('grid'); // grid | list

    const filtered = books.filter(b => {
        const matchesSearch = b.books_title.toLowerCase().includes(search.toLowerCase()) || b.id.includes(search);
        const matchesStatus = statusFilter === "All" ||
            (statusFilter === "Available" && b.Status === "Available") ||
            (statusFilter === "Issued" && b.Status !== "Available");
        return matchesSearch && matchesStatus;
    });

    const handleAdd = async () => {
        if (!newBookTitle) return;
        await fetch(`${API_BASE}/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newBookTitle })
        });
        setIsAddModalOpen(false);
        setNewBookTitle("");
        refresh();
    };

    return (
        <div className="space-y-6 animate-fade-in pl-0 lg:pl-6 max-w-7xl mx-auto">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end pb-6 border-b border-slate-200 dark:border-white/5 gap-4">
                <div>
                    <h1 className="text-4xl font-bold font-heading text-slate-900 dark:text-white mb-2 tracking-tight">Library Books</h1>
                    <p className="text-slate-500 dark:text-slate-400">Manage collection and track availability.</p>
                </div>
                {user.role === 'admin' && (
                    <Button onClick={() => setIsAddModalOpen(true)} className="w-full md:w-auto">
                        <Icon name="plus" size={20} /> Add New Book
                    </Button>
                )}
            </header>

            <div className="flex flex-col md:flex-row gap-4 mb-8">
                <div className="relative flex-1">
                    <Icon name="search" className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Search by title, ID..."
                        className="w-full bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-xl pl-12 pr-4 py-4 text-slate-900 dark:text-white outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-800"
                    />
                </div>
                <div className="flex gap-2">
                    <select
                        value={statusFilter}
                        onChange={e => setStatusFilter(e.target.value)}
                        className="bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-white outline-none focus:border-primary"
                    >
                        <option value="All">All Status</option>
                        <option value="Available">Available</option>
                        <option value="Issued">Issued</option>
                    </select>
                </div>
                <div className="flex bg-slate-100 dark:bg-slate-800/50 rounded-xl p-1 border border-slate-200 dark:border-slate-700/50">
                    <button onClick={() => setView('grid')} className={`p-3 rounded-lg transition-all ${view === 'grid' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}`}>
                        <Icon name="layout-grid" size={20} />
                    </button>
                    <button onClick={() => setView('list')} className={`p-3 rounded-lg transition-all ${view === 'list' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}`}>
                        <Icon name="list" size={20} />
                    </button>
                </div>
            </div>

            {view === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {filtered.map(book => (
                        <GlassCard key={book.id} className="group flex flex-col relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-slate-300 dark:bg-slate-700 group-hover:bg-accent transition-colors"></div>
                            <div className="flex justify-between items-start mb-4 pl-3">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-mono text-xs shadow-inner">
                                    #{book.id}
                                </div>
                                <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${book.Status === 'Available'
                                        ? 'bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20'
                                        : 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20'
                                    }`}>
                                    {book.Status === 'Available' ? 'In Stock' : 'Issued'}
                                </span>
                            </div>

                            <div className="pl-3 mb-6 min-h-[4rem] flex flex-col justify-center">
                                <h3 className="font-bold text-lg text-slate-900 dark:text-white leading-tight line-clamp-2 group-hover:text-accent transition-colors">{book.books_title}</h3>
                            </div>

                            {book.Status !== 'Available' && (
                                <div className="pl-3 mb-6 p-3 rounded-lg bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 mx-3 md:mx-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Icon name="user" size={12} className="text-slate-500 dark:text-slate-400" />
                                        <p className="text-xs text-slate-600 dark:text-slate-300 truncate">{book.lender_name}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Icon name="clock" size={12} className="text-slate-500 dark:text-slate-400" />
                                        <p className="text-xs text-slate-500">{book.Issue_date}</p>
                                    </div>
                                </div>
                            )}

                            <div className="mt-auto pl-3 pt-4 flex gap-2 border-t border-slate-200 dark:border-white/5">
                                {book.Status === 'Available' ? (
                                    <button onClick={() => onIssue(book.id)} className="flex-1 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-all text-sm font-bold shadow-lg shadow-indigo-500/20 active:translate-y-0.5">
                                        Issue Book
                                    </button>
                                ) : (
                                    <button onClick={() => onReturn(book.id)} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 hover:text-slate-900 dark:hover:text-white transition-all text-sm font-semibold active:translate-y-0.5">
                                        Return
                                    </button>
                                )}
                                {user.role === 'admin' && (
                                    <button onClick={() => onDelete(book.id)} className="p-2.5 rounded-lg bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white transition-all border border-red-500/20 hover:border-red-500">
                                        <Icon name="trash-2" size={18} />
                                    </button>
                                )}
                            </div>
                        </GlassCard>
                    ))}
                </div>
            ) : (
                <div className="glass-card rounded-2xl overflow-hidden border border-slate-200 dark:border-white/5">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-slate-200 dark:border-white/5 text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider bg-black/5 dark:bg-white/5">
                                <th className="p-4">ID</th>
                                <th className="p-4">Title</th>
                                <th className="p-4">Status</th>
                                <th className="p-4">Issued To</th>
                                <th className="p-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 dark:divide-white/5">
                            {filtered.map(book => (
                                <tr key={book.id} className="hover:bg-black/5 dark:hover:bg-white/5 transition-colors group">
                                    <td className="p-4 font-mono text-slate-500 dark:text-slate-400">#{book.id}</td>
                                    <td className="p-4 font-medium text-slate-900 dark:text-white group-hover:text-accent transition-colors">{book.books_title}</td>
                                    <td className="p-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${book.Status === 'Available' ? 'bg-green-400/10 text-green-600 dark:text-green-400' : 'bg-red-400/10 text-red-600 dark:text-red-400'
                                            }`}>
                                            {book.Status === 'Available' ? '● Available' : '● Issued'}
                                        </span>
                                    </td>
                                    <td className="p-4 text-slate-500 dark:text-slate-400 text-sm">{book.lender_name || '-'}</td>
                                    <td className="p-4 text-right flex justify-end gap-2">
                                        {book.Status === 'Available' ? (
                                            <button onClick={() => onIssue(book.id)} className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-white hover:bg-indigo-100 dark:hover:bg-indigo-600 px-3 py-1 rounded-md text-sm font-medium transition-all">Issue</button>
                                        ) : (
                                            <button onClick={() => onReturn(book.id)} className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-600 px-3 py-1 rounded-md text-sm font-medium transition-all">Return</button>
                                        )}
                                        {user.role === 'admin' && (
                                            <button onClick={() => onDelete(book.id)} className="text-red-400 hover:text-red-500 p-1.5 transition-colors">
                                                <Icon name="trash-2" size={16} />
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <Modal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} title="Add New Book">
                <Input label="Book Title" value={newBookTitle} onChange={e => setNewBookTitle(e.target.value)} placeholder="Enter full book title" required />
                <div className="flex justify-end gap-3 mt-8">
                    <Button variant="ghost" onClick={() => setIsAddModalOpen(false)}>Cancel</Button>
                    <Button onClick={handleAdd}>Save to Library</Button>
                </div>
            </Modal>
        </div>
    );
};

const HistoryLog = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        fetch(`${API_BASE}/history`)
            .then(res => res.json())
            .then(data => setLogs(data))
            .catch(err => console.error(err));
    }, []);

    return (
        <div className="space-y-6 animate-fade-in pl-0 lg:pl-6 max-w-7xl mx-auto">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end pb-6 border-b border-slate-200 dark:border-white/5 gap-4">
                <div>
                    <h1 className="text-4xl font-bold font-heading text-slate-900 dark:text-white mb-2 tracking-tight">Issue History</h1>
                    <p className="text-slate-500 dark:text-slate-400">Log of all library transactions.</p>
                </div>
            </header>

            <GlassCard className="p-0 overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-black/5 dark:bg-white/5 border-b border-slate-200 dark:border-white/5 text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider">
                            <th className="p-4">Date</th>
                            <th className="p-4">User</th>
                            <th className="p-4">Action</th>
                            <th className="p-4">Book</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-white/5">
                        {logs.map((log, i) => (
                            <tr key={i} className="hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                                <td className="p-4 text-xs font-mono text-slate-500 dark:text-slate-400 whitespace-nowrap">{log.date}</td>
                                <td className="p-4 text-sm font-medium text-slate-900 dark:text-white">{log.user}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${log.action === 'issued' ? 'bg-orange-500/10 text-orange-600 dark:text-orange-400' : 'bg-green-500/10 text-green-600 dark:text-green-400'
                                        }`}>
                                        {log.action}
                                    </span>
                                </td>
                                <td className="p-4 text-sm text-slate-700 dark:text-slate-300">{log.book}</td>
                            </tr>
                        ))}
                        {logs.length === 0 && (
                            <tr>
                                <td colSpan="4" className="p-8 text-center text-slate-500">No history found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </GlassCard>
        </div>
    );
};

const StudentProfile = ({ user, books }) => {
    return (
        <div className="space-y-8 animate-fade-in pl-0 lg:pl-6 max-w-7xl mx-auto">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end pb-6 border-b border-slate-200 dark:border-white/5">
                <div>
                    <h1 className="text-4xl font-bold font-heading text-slate-900 dark:text-white mb-2 tracking-tight">My Profile</h1>
                    <p className="text-slate-500 dark:text-slate-400">Manage your account and viewing history.</p>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <GlassCard className="md:col-span-1 flex flex-col items-center text-center p-8 bg-gradient-to-b from-white/20 dark:from-white/5 to-transparent">
                    <div className="w-32 h-32 rounded-full p-1 bg-gradient-to-tr from-accent to-primary mb-6 animate-pulse-slow">
                        <div className="w-full h-full rounded-full bg-slate-200 dark:bg-slate-900 flex items-center justify-center overflow-hidden">
                            <Icon name="user" size={60} className="text-slate-400 dark:text-slate-300" />
                        </div>
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{user.name}</h2>
                    <p className="text-accent font-mono text-sm mb-6">{user.email}</p>

                    <div className="w-full grid grid-cols-2 gap-4 border-t border-slate-200 dark:border-white/10 pt-6">
                        <div>
                            <p className="text-slate-500 text-xs uppercase font-bold tracking-wider">Role</p>
                            <p className="text-slate-900 dark:text-white font-medium">{user.role}</p>
                        </div>
                        <div>
                            <p className="text-slate-500 text-xs uppercase font-bold tracking-wider">ID</p>
                            <p className="text-slate-900 dark:text-white font-medium">{user.id}</p>
                        </div>
                    </div>
                </GlassCard>

                <div className="md:col-span-2 space-y-6">
                    <h3 className="font-bold text-xl text-slate-900 dark:text-white">Current Loans</h3>
                    <div className="p-6 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center text-center min-h-[200px]">
                        <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4 text-slate-400 dark:text-slate-500">
                            <Icon name="book" size={24} />
                        </div>
                        <p className="text-slate-500 dark:text-slate-400 max-w-sm">
                            Your borrowing history is tracked by the librarian.
                            <br />Please contact the desk to see checking details.
                        </p>
                    </div>

                    <h3 className="font-bold text-xl text-slate-900 dark:text-white pt-4">Recommended for You</h3>
                    <div className="grid grid-cols-2 gap-4">
                        {books.sort(() => 0.5 - Math.random()).slice(0, 2).map(b => (
                            <GlassCard key={b.id} className="p-4 flex items-center gap-4 hover:border-accent/40">
                                <div className="h-16 w-12 bg-slate-200 dark:bg-slate-700 rounded shadow-md flex-shrink-0"></div>
                                <div>
                                    <h4 className="font-bold text-slate-900 dark:text-white text-sm line-clamp-1">{b.books_title}</h4>
                                    <p className="text-xs text-slate-500 mt-1">Trending now</p>
                                </div>
                            </GlassCard>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- 5. App Shell ---

const AppContent = () => {
    const { user, logout } = useAuth();
    const [tab, setTab] = useState('dashboard');
    const { books, stats, refresh } = useBooks();

    const [issueModalOpen, setIssueModalOpen] = useState(false);
    const [selectedBookId, setSelectedBookId] = useState(null);
    const [borrowerName, setBorrowerName] = useState(user.name || "");

    const handleIssueFlow = (id) => {
        setSelectedBookId(id);
        // If student, autofill name
        setBorrowerName(user.name);
        setIssueModalOpen(true);
    };

    const handleReturnFlow = async (id) => {
        if (!confirm("Return this book?")) return;
        try {
            const res = await fetch(`${API_BASE}/return`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ book_id: id })
            });
            const data = await res.json();
            if (data.success) {
                refresh();
            } else {
                alert(data.message);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure you want to delete this book?")) return;
        await fetch(`${API_BASE}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'role': user.role
            },
            body: JSON.stringify({ book_id: id, confirm: 'y' })
        });
        refresh();
    };

    const confirmIssue = async () => {
        if (!borrowerName) return;
        try {
            const res = await fetch(`${API_BASE}/issue`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ book_id: selectedBookId, user_name: borrowerName })
            });
            const data = await res.json();
            if (data.success) {
                setIssueModalOpen(false);
                refresh();
            } else {
                alert("Error: " + data.message);
            }
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="min-h-screen bg-transparent text-slate-900 dark:text-white font-sans selection:bg-accent/30 selection:text-white flex transition-colors duration-500">
            {/* Ambient Background */}
            <div className="fixed inset-0 pointer-events-none z-[-1] opacity-50 dark:opacity-100 transition-opacity">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/10 dark:bg-indigo-900/20 rounded-full blur-[120px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-cyan-500/10 dark:bg-cyan-900/20 rounded-full blur-[120px] animate-pulse-slow"></div>
            </div>

            <Sidebar activeTab={tab} onChangeTab={setTab} user={user} onLogout={logout} />

            <main className="flex-1 ml-20 lg:ml-72 p-4 lg:p-8 transition-all overflow-x-hidden">
                {tab === 'dashboard' && <Dashboard stats={stats} user={user} />}
                {tab === 'books' && <BookList books={books} refresh={refresh} onIssue={handleIssueFlow} onReturn={handleReturnFlow} onDelete={handleDelete} user={user} />}
                {tab === 'student' && <StudentProfile user={user} books={books} />}
                {tab === 'history' && <HistoryLog />}
            </main>

            <Modal isOpen={issueModalOpen} onClose={() => setIssueModalOpen(false)} title="Issue Book">
                <p className="mb-6 text-slate-500 dark:text-slate-400 text-sm">Review details before confirming the issue of this book.</p>

                <div className="bg-slate-100 dark:bg-slate-800/50 p-4 rounded-xl mb-6 border border-slate-200 dark:border-white/5">
                    <p className="text-xs uppercase font-bold text-slate-500 mb-1">Book ID</p>
                    <p className="font-mono text-slate-900 dark:text-white mb-3">#{selectedBookId}</p>
                    <p className="text-xs uppercase font-bold text-slate-500 mb-1">Issuer</p>
                    <p className="font-medium text-slate-900 dark:text-white">{borrowerName}</p>
                </div>

                {user.role === 'admin' && (
                    <Input label="Confirm Borrower Name" value={borrowerName} onChange={e => setBorrowerName(e.target.value)} />
                )}

                <div className="flex justify-end gap-3 mt-6">
                    <Button variant="ghost" onClick={() => setIssueModalOpen(false)}>Cancel</Button>
                    <Button onClick={confirmIssue}>Confirm Issue</Button>
                </div>
            </Modal>
        </div>
    );
};

// --- 6. ChatBot Component ---
const ChatBot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { id: 1, text: "Hi! I'm your AI Librarian. Ask me about books, characters, or plot points!", sender: 'bot' }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsTyping(true);

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.text })
            });
            const data = await res.json();

            const botMsg = { id: Date.now() + 1, text: data.response, sender: 'bot' };
            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            setMessages(prev => [...prev, { id: Date.now() + 1, text: "Sorry, I'm having trouble thinking right now.", sender: 'bot' }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            {isOpen && (
                <div className="glass-card w-80 md:w-96 mb-4 rounded-2xl shadow-2xl border border-white/20 dark:border-white/10 flex flex-col overflow-hidden animate-scale-up origin-bottom-right bg-white/90 dark:bg-black/40">
                    <div className="bg-gradient-to-r from-primary to-accent p-4 flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                                <Icon name="bot" className="text-white" size={18} />
                            </div>
                            <div>
                                <h3 className="font-bold text-white text-sm">AI Librarian</h3>
                                <p className="text-[10px] text-white/80 flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span> Online
                                </p>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-white/80 hover:text-white">
                            <Icon name="x" size={18} />
                        </button>
                    </div>

                    <div className="h-80 overflow-y-auto p-4 space-y-3 bg-slate-50 dark:bg-slate-900/80 backdrop-blur-md">
                        {messages.map(msg => (
                            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] p-3 rounded-2xl text-sm shadow-sm ${msg.sender === 'user'
                                        ? 'bg-primary text-white rounded-tr-none'
                                        : 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-tl-none'
                                    }`}>
                                    {msg.text}
                                    {msg.sender === 'bot' && (
                                        <div className="mt-2 flex gap-1">
                                            {/* Explainable AI Visual Badge */}
                                            {msg.text.includes("found") && <span className="text-[10px] bg-green-500/20 text-green-600 dark:text-green-400 px-1.5 py-0.5 rounded border border-green-500/20">Exact Match</span>}
                                            {msg.text.includes("interest in") && <span className="text-[10px] bg-accent/20 text-accent dark:text-cyan-300 px-1.5 py-0.5 rounded border border-accent/20">Smart Rec</span>}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className="bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none flex gap-1 items-center shadow-sm">
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                </div>
                            </div>
                        )}
                    </div>

                    <form onSubmit={handleSend} className="p-3 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-white/5 flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder="Ask about a book..."
                            className="flex-1 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white outline-none focus:border-accent"
                        />
                        <button type="submit" disabled={!input || isTyping} className="bg-accent text-slate-900 p-2 rounded-xl hover:opacity-90 disabled:opacity-50 transition-all">
                            <Icon name="send" size={18} />
                        </button>
                    </form>
                </div>
            )}

            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-14 h-14 rounded-full bg-gradient-to-tr from-primary to-accent shadow-lg shadow-primary/40 flex items-center justify-center text-white hover:scale-110 active:scale-95 transition-all group relative"
            >
                {isOpen ? <Icon name="x" size={24} /> : <Icon name="message-circle" size={24} />}
                {!isOpen && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-slate-900 animate-bounce"></span>
                )}
            </button>
        </div>
    );
};

// --- 7. Theme & Auth Providers ---

const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState('dark');

    useEffect(() => {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);

    const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    const login = (userData) => {
        setUser(userData);
    };

    const logout = () => {
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {user ? (
                <>
                    <AppContent />
                    <ChatBot />
                </>
            ) : <Login />}
        </AuthContext.Provider>
    );
};

const App = () => {
    return (
        <ThemeProvider>
            <AuthProvider />
        </ThemeProvider>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
