/**
 * Task Manager — React frontend (single file, CDN)
 * Authored by: dev_frontend agent (dev_agency company plugin)
 * Review: tech_lead
 *
 * Uses React 18 via CDN + Babel standalone for JSX transpilation.
 */

const API = window.API_BASE_URL || "";
const { useState, useEffect, useCallback, useRef, createContext, useContext } = React;

// ─── Auth Context ──────────────────────────────────────────────────────────
const AuthContext = createContext(null);

function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem("tm_token") || null);
    const [user, setUser] = useState(localStorage.getItem("tm_user") || null);

    const login = useCallback((newToken, username) => {
        localStorage.setItem("tm_token", newToken);
        localStorage.setItem("tm_user", username);
        setToken(newToken);
        setUser(username);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem("tm_token");
        localStorage.removeItem("tm_user");
        setToken(null);
        setUser(null);
    }, []);

    return React.createElement(AuthContext.Provider, { value: { token, user, login, logout } }, children);
}

function useAuth() { return useContext(AuthContext); }

// ─── API helpers ───────────────────────────────────────────────────────────
async function api(path, opts = {}) {
    const token = localStorage.getItem("tm_token");
    const headers = { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(opts.headers || {}) };
    const res = await fetch(`${API}${path}`, { ...opts, headers });
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    return data;
}

// ─── AuthPage ──────────────────────────────────────────────────────────────
function AuthPage() {
    const [mode, setMode] = useState("login"); // login | register
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            if (mode === "register") {
                const data = await api("/auth/register", {
                    method: "POST",
                    body: JSON.stringify({ username, email, password }),
                });
                login(data.access_token, username);
            } else {
                const data = await api("/auth/login", {
                    method: "POST",
                    body: JSON.stringify({ username, password }),
                });
                login(data.access_token, username);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    return React.createElement("div", { className: "auth-page" },
        React.createElement("div", { className: "card auth-card" },
            React.createElement("h2", null, mode === "login" ? "Sign In" : "Create Account"),
            error && React.createElement("div", { className: "auth-error" }, error),
            React.createElement("form", { onSubmit: handleSubmit },
                React.createElement("div", { className: "form-group" },
                    React.createElement("label", null, "Username"),
                    React.createElement("input", {
                        className: "form-input", type: "text",
                        value: username, onChange: (e) => setUsername(e.target.value),
                        required: true, placeholder: "johndoe",
                        autoComplete: "username",
                    }),
                ),
                mode === "register" && React.createElement("div", { className: "form-group" },
                    React.createElement("label", null, "Email"),
                    React.createElement("input", {
                        className: "form-input", type: "email",
                        value: email, onChange: (e) => setEmail(e.target.value),
                        required: mode === "register", placeholder: "john@example.com",
                    }),
                ),
                React.createElement("div", { className: "form-group" },
                    React.createElement("label", null, "Password"),
                    React.createElement("input", {
                        className: "form-input", type: "password",
                        value: password, onChange: (e) => setPassword(e.target.value),
                        required: true, placeholder: "••••••••",
                        autoComplete: mode === "login" ? "current-password" : "new-password",
                    }),
                ),
                React.createElement("button", {
                    className: "btn btn-primary", style: { width: "100%", justifyContent: "center" },
                    type: "submit", disabled: loading,
                }, loading ? React.createElement("span", { className: "spinner" }) : (mode === "login" ? "Sign In" : "Register")),
                React.createElement("p", { style: { textAlign: "center", marginTop: "1rem", fontSize: "0.85rem", color: "#64748b" } },
                    mode === "login"
                        ? ["Don't have an account? ", React.createElement("a", { href: "#", style: { color: "#38bdf8" }, onClick: (e) => { e.preventDefault(); setMode("register"); } }, "Register")]
                        : ["Already have an account? ", React.createElement("a", { href: "#", style: { color: "#38bdf8" }, onClick: (e) => { e.preventDefault(); setMode("login"); } }, "Sign In")],
                ),
            ),
        ),
    );
}

// ─── TaskCard ──────────────────────────────────────────────────────────────
function TaskCard({ task, onUpdate, onDelete }) {
    const [updating, setUpdating] = useState(false);

    async function cycleStatus() {
        setUpdating(true);
        try {
            const next = { pending: "in_progress", in_progress: "completed", completed: "completed", cancelled: "pending" };
            await api(`/tasks/${task.id}/status?new_status=${next[task.status]}`, { method: "PATCH" });
            onUpdate();
        } finally { setUpdating(false); }
    }

    const dueText = task.due_date ? new Date(task.due_date).toLocaleDateString() : "";

    return React.createElement("div", { className: `task-item${task.status === "completed" ? " completed" : ""}` },
        React.createElement("div", { className: "task-main" },
            React.createElement("div", null,
                React.createElement("span", { className: `badge badge-${task.status.replace("/", "_")}` }, task.status.replace("_", " ")),
                React.createElement("span", { className: `badge badge-${task.priority}` }, task.priority),
            ),
            React.createElement("div", { className: "task-title", style: { marginTop: "0.3rem" } }, task.title),
            task.description && React.createElement("div", { className: "task-meta" }, task.description),
            React.createElement("div", { className: "task-meta", style: { marginTop: "0.2rem" } },
                dueText ? `Due: ${dueText}` : "",
            ),
        ),
        React.createElement("div", { className: "task-buttons" },
            React.createElement("button", { className: "btn btn-ghost btn-sm", disabled: updating, onClick: cycleStatus },
                updating ? React.createElement("span", { className: "spinner" }) : (task.status === "completed" ? "\u2714" : "\u25B6"),
            ),
            React.createElement("button", { className: "btn btn-ghost btn-sm", style: { color: "#f87171" }, onClick: () => onDelete(task.id) }, "\u2716"),
        ),
    );
}

// ─── TaskModal (create / edit) ─────────────────────────────────────────────
function TaskModal({ task, onClose, onSaved }) {
    const isEdit = !!task;
    const [title, setTitle] = useState(task?.title || "");
    const [description, setDescription] = useState(task?.description || "");
    const [priority, setPriority] = useState(task?.priority || "medium");
    const [dueDate, setDueDate] = useState(task?.due_date ? task.due_date.slice(0, 16) : "");
    const [error, setError] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");
        try {
            const payload = { title, description, priority, due_date: dueDate ? new Date(dueDate).toISOString() : null };
            if (isEdit) {
                await api(`/tasks/${task.id}`, { method: "PUT", body: JSON.stringify(payload) });
            } else {
                await api("/tasks", { method: "POST", body: JSON.stringify(payload) });
            }
            onSaved();
        } catch (err) { setError(err.message); }
    }

    const titleText = isEdit ? "Edit Task" : "New Task";

    return React.createElement("div", { className: "modal-overlay", onClick: (e) => { if (e.target === e.currentTarget) onClose(); } },
        React.createElement("div", { className: "card modal-card" },
            React.createElement("div", { className: "modal-header" },
                React.createElement("h3", null, titleText),
                React.createElement("button", { className: "close-x", onClick: onClose }, "\u2716"),
            ),
            error && React.createElement("div", { className: "auth-error" }, error),
            React.createElement("form", { onSubmit: handleSubmit },
                React.createElement("div", { className: "form-group" },
                    React.createElement("label", null, "Title"),
                    React.createElement("input", { className: "form-input", type: "text", value: title, onChange: (e) => setTitle(e.target.value), required: true, placeholder: "What needs to be done?" }),
                ),
                React.createElement("div", { className: "form-group" },
                    React.createElement("label", null, "Description"),
                    React.createElement("textarea", { className: "form-input", value: description, onChange: (e) => setDescription(e.target.value), placeholder: "Optional details..." }),
                ),
                React.createElement("div", { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" } },
                    React.createElement("div", { className: "form-group" },
                        React.createElement("label", null, "Priority"),
                        React.createElement("select", { className: "form-select", value: priority, onChange: (e) => setPriority(e.target.value) },
                            React.createElement("option", { value: "low" }, "Low"),
                            React.createElement("option", { value: "medium" }, "Medium"),
                            React.createElement("option", { value: "high" }, "High"),
                        ),
                    ),
                    React.createElement("div", { className: "form-group" },
                        React.createElement("label", null, "Due Date"),
                        React.createElement("input", { className: "form-input", type: "datetime-local", value: dueDate, onChange: (e) => setDueDate(e.target.value) }),
                    ),
                ),
                React.createElement("button", { className: "btn btn-primary", style: { width: "100%", justifyContent: "center" }, type: "submit" },
                    isEdit ? "Update Task" : "Create Task",
                ),
            ),
        ),
    );
}

// ─── ConfirmModal ──────────────────────────────────────────────────────────
function ConfirmModal({ message, onConfirm, onCancel }) {
    return React.createElement("div", { className: "modal-overlay", onClick: (e) => { if (e.target === e.currentTarget) onCancel(); } },
        React.createElement("div", { className: "card modal-card", style: { textAlign: "center" } },
            React.createElement("h3", { style: { marginBottom: "1rem", color: "#f87171" } }, "Confirm Delete"),
            React.createElement("p", { style: { marginBottom: "1.5rem", color: "#94a3b8" } }, message),
            React.createElement("div", { style: { display: "flex", gap: "0.5rem", justifyContent: "center" } },
                React.createElement("button", { className: "btn btn-ghost", onClick: onCancel }, "Cancel"),
                React.createElement("button", { className: "btn btn-danger", onClick: onConfirm }, "Delete"),
            ),
        ),
    );
}

// ─── Dashboard ─────────────────────────────────────────────────────────────
function Dashboard() {
    const { user, logout } = useAuth();
    const [tasks, setTasks] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState("");
    const [modalOpen, setModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [deleteTarget, setDeleteTarget] = useState(null);

    async function fetchData() {
        try {
            const [t, s] = await Promise.all([
                statusFilter ? api(`/tasks/filter?status_filter=${statusFilter}`) : api("/tasks"),
                api("/stats/summary"),
            ]);
            setTasks(t);
            setStats(s);
        } catch (err) { /* ignore */ }
        setLoading(false);
    }

    useEffect(() => { fetch(); }, []);
    // eslint-disable-next-line
    function fetch() { setLoading(true); fetchData(); }

    async function handleDelete(id) {
        try {
            await api(`/tasks/${id}`, { method: "DELETE" });
            setDeleteTarget(null);
            fetch();
        } catch (err) { alert(err.message); }
    }

    function openEdit(task) { setEditingTask(task); setModalOpen(true); }
    function openNew() { setEditingTask(null); setModalOpen(true); }

    return React.createElement("div", { className: "dashboard" },
        // Header
        React.createElement("header", { className: "header" },
            React.createElement("div", { className: "header-inner" },
                React.createElement("span", { className: "header-logo" }, "\u2705 Task Manager"),
                React.createElement("div", { className: "user-bar" },
                    React.createElement("span", null, `Hello, ${user}`),
                    React.createElement("button", { className: "btn btn-ghost btn-sm", onClick: logout }, "Logout"),
                ),
            ),
        ),
        React.createElement("div", { className: "container" },
            // Stats
            stats && React.createElement("div", { className: "stats-row" },
                ["pending", "in_progress", "completed", "high_priority"].map((k) =>
                    React.createElement("div", { className: "card stat-card" },
                        React.createElement("div", { className: "stat-number" }, stats[k]),
                        React.createElement("div", { className: "stat-label" }, k.replace("_", " ")),
                    ),
                ),
            ),
            // Toolbar
            React.createElement("div", { className: "task-toolbar" },
                React.createElement("div", { className: "task-actions-bar" },
                    React.createElement("select", {
                        className: "form-select filter-select",
                        value: statusFilter,
                        onChange: (e) => { setStatusFilter(e.target.value); fetch(); },
                    },
                        React.createElement("option", { value: "" }, "All"),
                        React.createElement("option", { value: "pending" }, "Pending"),
                        React.createElement("option", { value: "in_progress" }, "In Progress"),
                        React.createElement("option", { value: "completed" }, "Completed"),
                        React.createElement("option", { value: "cancelled" }, "Cancelled"),
                    ),
                ),
                React.createElement("button", { className: "btn btn-primary", onClick: openNew }, "+ New Task"),
            ),
            // List
            loading
                ? React.createElement("div", { className: "spinner-wrap" }, React.createElement("span", { className: "spinner" }))
                : tasks.length === 0
                    ? React.createElement("div", { className: "empty" },
                        'No tasks yet. Click \u201c+ New Task\u201d to create one.',
                    )
                    : React.createElement("div", { className: "task-list" },
                        tasks.map((t) =>
                            React.createElement(TaskCard, {
                                key: t.id,
                                task: t,
                                onUpdate: fetch,
                                onDelete: (id) => setDeleteTarget(id),
                            }),
                        ),
                    ),

            // Modals
            modalOpen && React.createElement(TaskModal, {
                task: editingTask,
                onClose: () => setModalOpen(false),
                onSaved: () => { setModalOpen(false); fetch(); },
            }),
            deleteTarget && React.createElement(ConfirmModal, {
                message: "Are you sure you want to delete this task? This cannot be undone.",
                onConfirm: () => handleDelete(deleteTarget),
                onCancel: () => setDeleteTarget(null),
            }),
        ),
    );
}

// ─── App ───────────────────────────────────────────────────────────────────
function App() {
    const { token } = useAuth();
    return token ? React.createElement(Dashboard) : React.createElement(AuthPage);
}

// ─── Mount ─────────────────────────────────────────────────────────────────
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(React.createElement(AuthProvider, null, React.createElement(App)));
