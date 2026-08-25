import { useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export default function AiLibrarianPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", text: "Hi! Ask me for book recommendations by title, author, or topic." },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = input;
    setMessages((m) => [...m, { role: "user", text: userMessage }]);
    setInput("");
    setSending(true);
    try {
      const data = await api.post<{ response: string }>("/ai/chat", { message: userMessage });
      setMessages((m) => [...m, { role: "assistant", text: data.response }]);
    } catch (err) {
      const text = err instanceof ApiError ? err.message : "Something went wrong.";
      setMessages((m) => [...m, { role: "assistant", text }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div>
      <h1>AI Librarian</h1>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.text}
          </div>
        ))}
        {sending && <div className="chat-bubble assistant">…</div>}
      </div>
      <form className="search-bar" onSubmit={handleSubmit}>
        <input
          placeholder="Ask about a book, genre, or author…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" disabled={sending}>
          Send
        </button>
      </form>
    </div>
  );
}
