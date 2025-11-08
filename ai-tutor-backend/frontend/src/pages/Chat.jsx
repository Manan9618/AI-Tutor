// src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from "react";
import {
  getChatResponse,
  getChatHistory,
  getChatSessions,
  clearChatHistory,
  updateAnalytics,
} from "../api/api";
import "./Chat.css";

const Chat = () => {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeChatId, setActiveChatId] = useState(null); // session_id from DB
  const [chats, setChats] = useState([]); // fetched sessions list
  const chatEndRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // Load chat sessions list on mount
  useEffect(() => {
    loadChatSessions();
  }, []);

  const loadChatSessions = async () => {
    try {
      const res = await getChatSessions();
      setChats(res.data.sessions || []);
    } catch (err) {
      console.error("Failed to load chat sessions:", err);
      setError("Failed to load chat sessions");
    }
  };

  const loadChatHistory = async (sessionId) => {
    try {
      const res = await getChatHistory(sessionId);
      setChatHistory(res.data.history || []);
    } catch (err) {
      console.error("Failed to load chat history:", err);
      setError("Failed to load chat history");
    }
  };

  const handleSend = async () => {
    if (!message.trim()) return;

    setError("");
    const userMessage = message;
    setMessage("");
    const newMessage = {
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setChatHistory((prev) => [...prev, newMessage]);
    setIsLoading(true);

    try {
      // ✅ Send message (activeChatId = session_id)
      const res = await getChatResponse(userMessage, activeChatId);
      const aiReply = res.data.response || "No response received";
      const sessionId = res.data.session_id;

      // Save new session if it's newly created
      if (!activeChatId) {
        setActiveChatId(sessionId);
        await loadChatSessions();
      }

      const aiMessage = {
        role: "assistant",
        content: aiReply,
        timestamp: new Date().toISOString(),
      };

      setChatHistory((prev) => [...prev, aiMessage]);

      // ✅ Update analytics
      await updateAnalytics({
        type: "chat",
        status: "sent",
      });
    } catch (err) {
      setError("Failed to get response. Please try again.");
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearHistory = async () => {
    if (!activeChatId) return;
    if (window.confirm("Are you sure you want to clear this chat?")) {
      try {
        await clearChatHistory(activeChatId);
        setChatHistory([]);
      } catch (err) {
        console.error("Failed to clear history:", err);
      }
    }
  };

  const startNewChat = () => {
    setActiveChatId(null);
    setChatHistory([]);
    setMessage("");
  };

  const selectChat = async (id) => {
    setActiveChatId(id);
    setChatHistory([]);
    await loadChatHistory(id);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="chat-page">
      {/* Header */}
      <div className="chat-header">
        <div className="header-title">
          <span>💬</span> Chat with AI Tutor
        </div>
        <button onClick={startNewChat} className="new-chat-btn">
          + New Chat
        </button>
      </div>

      {/* Main Container */}
      <div className="chat-main-container">
        {/* Sidebar */}
        <div className="chat-sidebar">
          <div className="sidebar-header">
            <h3>Chats</h3>
          </div>
          <div className="chat-list">
            {chats.length === 0 ? (
              <div className="empty-state">
                <p>No chats yet. Start a new one!</p>
              </div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.session_id}
                  className={`chat-item ${
                    chat.session_id === activeChatId ? "active" : ""
                  }`}
                  onClick={() => selectChat(chat.session_id)}
                >
                  <div className="chat-icon">💬</div>
                  <div className="chat-info">
                    <div className="chat-title">
                      {chat.title || "Untitled Chat"}
                    </div>
                    <div className="chat-date">
                      {new Date(chat.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="chat-area">
          {/* Chat Header */}
          <div className="chat-area-header">
            <h4>
              {activeChatId
                ? `Chat #${activeChatId}`
                : "New Chat"}
            </h4>
            <span>{chatHistory.length} messages</span>
            {activeChatId && (
              <button
                onClick={handleClearHistory}
                className="clear-chat-btn"
              >
                🗑️ Clear
              </button>
            )}
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {chatHistory.length === 0 ? (
              <div className="empty-state">
                <p>👋 Hello! How can I assist you with your learning today?</p>
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
                <div key={idx} className={`message-bubble ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === "user" ? "👤" : "🧠"}
                  </div>
                  <div className="message-content">
                    <p>{msg.content}</p>
                    <div className="message-timestamp">
                      {formatTime(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="message-bubble assistant">
                <div className="message-avatar">🧠</div>
                <div className="message-content">
                  <p className="typing-indicator">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input-wrapper">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your question... (Press Enter to send)"
              disabled={isLoading}
              rows="1"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !message.trim()}
              className="send-btn"
            >
              ➤ Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;