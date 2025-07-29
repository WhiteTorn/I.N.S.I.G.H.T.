// API service for INSIGHT backend communication
const API_BASE_URL = 'http://localhost:8000';

export interface BriefingRequest {
  date: string; // Format: "YYYY-MM-DD"
}

export interface BriefingResponse {
  success: boolean;
  briefing?: string; // AI-generated briefing content
  date?: string;
  posts_processed?: number;
  total_posts_fetched?: number;
  error?: string;
}

export interface SourceStats {
  success: boolean;
  data?: Record<string, any>;
  error?: string;
}

class ApiService {
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async generateBriefing(date: string): Promise<BriefingResponse> {
    try {
      const response = await this.makeRequest<BriefingResponse>('/api/daily', {
        method: 'POST',
        body: JSON.stringify({ date }),
      });
      
      return response;
    } catch (error) {
      console.error('Failed to generate briefing:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async getEnabledSources(): Promise<SourceStats> {
    try {
      const response = await this.makeRequest<SourceStats>('/api/enabled-sources');
      return response;
    } catch (error) {
      console.error('Failed to get enabled sources:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch sources'
      };
    }
  }

  async getSources(): Promise<SourceStats> {
    try {
      const response = await this.makeRequest<SourceStats>('/api/sources');
      return response;
    } catch (error) {
      console.error('Failed to get sources:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch sources'
      };
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService; 