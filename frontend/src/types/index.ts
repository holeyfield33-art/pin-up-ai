export interface Snippet {
  id: string;
  title: string;
  body: string;
  language: string;
  source?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  tags: Tag[];
  collections: Collection[];
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  created_at: string;
  snippet_count?: number;
}

export interface Collection {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  color: string;
  created_at: string;
  updated_at: string;
  snippet_count?: number;
}

export interface SnippetCreateInput {
  title: string;
  body: string;
  language?: string;
  source?: string;
  tag_ids?: string[];
  collection_ids?: string[];
}

export interface AppState {
  snippets: Snippet[];
  selectedSnippet: Snippet | null;
  tags: Tag[];
  collections: Collection[];
  loading: boolean;
  error: string | null;
  backendStatus: 'checking' | 'connected' | 'error' | 'disconnected';
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}
