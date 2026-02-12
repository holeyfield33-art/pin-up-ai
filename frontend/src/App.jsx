import { useState } from "react";
import { api } from "./api";
import "./App.css";

function App() {
  const [greetMsg, setGreetMsg] = useState("");
  const [name, setName] = useState("");

  async function greet() {
    const res = await api("/health");
    setGreetMsg(`Hello, ${name || "World"}! Backend status: ${res.status}`);
  }

  return (
    <div className="container mx-auto p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-slate-100">📌 Pin-Up AI</h1>
        <p className="text-slate-300 mb-6">
          Save and organize the best AI messages
        </p>

        <div className="space-y-4">
          <input
            id="greet-input"
            onChange={(e) => setName(e.currentTarget.value)}
            placeholder="Enter a name..."
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500"
          />
          <button
            onClick={() => greet()}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition"
          >
            Greet
          </button>
        </div>

        {greetMsg && (
          <div className="mt-6 p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-100">
            {greetMsg}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
