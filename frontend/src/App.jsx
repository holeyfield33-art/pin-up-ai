import { useState, useEffect } from "react";
import { snippetsAPI, tagsAPI, collectionsAPI } from "./api";
import SearchBar from "./components/SearchBar";
import Sidebar from "./components/Sidebar";
import SnippetList from "./components/SnippetList";
import SnippetDetail from "./components/SnippetDetail";
import "./App.css";

function App() {
  const [snippets, setSnippets] = useState([]);
  const [selectedSnippet, setSelectedSnippet] = useState(null);
  const [tags, setTags] = useState([]);
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking");

  //Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [snippetsData, tagsData, collectionsData] = await Promise.all([
          snippetsAPI.list(),
          tagsAPI.list(),
          collectionsAPI.list(),
        ]);
        
        setSnippets(snippetsData);
        setTags(tagsData);
        setCollections(collectionsData);
        setBackendStatus("connected");
        setError(null);
      } catch (err) {
        setError(`Failed to load data: ${err.message}`);
        setBackendStatus("error");
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  // Handle search
  const handleSearch = async (query) => {
    if (!query.trim()) {
      const data = await snippetsAPI.list();
      setSnippets(data);
      return;
    }
    
    try {
      setLoading(true);
      const results = await snippetsAPI.search(query);
      setSnippets(results);
    } catch (err) {
      setError(`Search failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle collection filter
  const handleSelectCollection = async (collectionId) => {
    try {
      setLoading(true);
      const data = await snippetsAPI.list(50, 0, collectionId);
      setSnippets(data);
    } catch (err) {
      setError(`Failed to load: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDeleteSnippet = async (id) => {
    if (!confirm("Delete this snippet?")) return;
    try {
      await snippetsAPI.delete(id);
      setSnippets(snippets.filter((s) => s.id !== id));
      if (selectedSnippet?.id === id) setSelectedSnippet(null);
    } catch (err) {
      setError(`Failed to delete: ${err.message}`);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      <Sidebar tags={tags} collections={collections} onSelectCollection={handleSelectCollection} statusIndicator={backendStatus} />
      
      <div className="flex-1 flex flex-col">
        <div className="bg-slate-900 border-b border-slate-800 p-4">
          <h1 className="text-3xl font-bold mb-4">📌 Pin-Up AI</h1>
          <SearchBar onSearch={handleSearch} />
        </div>

        {error && <div className="bg-red-900/20 border border-red-700 text-red-200 px-4 py-3 m-4 rounded">{error}</div>}

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 border-r border-slate-800 overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-slate-400">Loading...</div>
            ) : snippets.length === 0 ? (
              <div className="p-8 text-center text-slate-400">No snippets</div>
            ) : (
              <SnippetList snippets={snippets} selectedId={selectedSnippet?.id} onSelect={setSelectedSnippet} />
            )}
          </div>

          <div className="w-96 border-l border-slate-800 overflow-y-auto hidden md:block">
            {selectedSnippet ? (
              <SnippetDetail snippet={selectedSnippet} onDelete={() => handleDeleteSnippet(selectedSnippet.id)} />
            ) : (
              <div className="p-8 text-center text-slate-400">Select a snippet</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
