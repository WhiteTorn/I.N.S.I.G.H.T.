export interface SourceConfig {
  metadata: {
    name: string;
    description: string;
    version: string;
  };
  platforms: {
    [key: string]: {
      enabled: boolean;
      sources: string[];
    };
  };
}

export interface BriefingResponse {
  success: boolean;
  briefing?: string;
  date: string;
  posts_processed: number;
  total_posts_fetched: number;
  error?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
} 