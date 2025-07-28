import { SourceConfig, BriefingResponse, ApiResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
  }

  async getSources(): Promise<ApiResponse<SourceConfig>> {
    return this.request<ApiResponse<SourceConfig>>('/sources');
  }

  async updateSources(config: SourceConfig): Promise<ApiResponse> {
    return this.request<ApiResponse>('/sources', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async generateBriefing(date: string): Promise<BriefingResponse> {
    return this.request<BriefingResponse>('/daily', {
      method: 'POST',
      body: JSON.stringify({ date }),
    });
  }
}

export const apiClient = new ApiClient(); 