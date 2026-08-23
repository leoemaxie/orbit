import type {
	AutomationListOut,
	AutomationOut,
	GoalRequest,
	HealthStatus,
	RunOut
} from './types';

// Read API URL from Vite import.meta.env, only defaulting to localhost / relative /api/v1 if PUBLIC_API_URL is empty
export const API_BASE = (typeof import.meta !== 'undefined' && import.meta.env?.PUBLIC_API_URL && import.meta.env.PUBLIC_API_URL.trim() !== '') 
	? import.meta.env.PUBLIC_API_URL.replace(/\/+$/, '')
	: (typeof window !== 'undefined' ? '/api/v1' : 'http://localhost:8000/api/v1');

export class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE) {
		this.baseUrl = baseUrl;
	}

	private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
		const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
		const url = `${this.baseUrl}${cleanEndpoint}`;

		const headers: HeadersInit = {
			'Content-Type': 'application/json',
			Accept: 'application/json',
			...options.headers
		};

		const response = await fetch(url, {
			...options,
			headers
		});

		if (!response.ok) {
			let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
			try {
				const errorJson = await response.json();
				if (errorJson.detail) {
					errorMessage = typeof errorJson.detail === 'string' 
						? errorJson.detail 
						: JSON.stringify(errorJson.detail);
				}
			} catch {
				// use default errorMessage
			}
			throw new Error(errorMessage);
		}

		// Check for empty responses (e.g. 204 or DELETE)
		const text = await response.text();
		return text ? JSON.parse(text) : ({} as T);
	}

	// Health check
	async getHealth(): Promise<HealthStatus> {
		return this.request<HealthStatus>('/health');
	}

	// Automations
	async listAutomations(): Promise<AutomationListOut> {
		return this.request<AutomationListOut>('/automations');
	}

	async getAutomation(id: string): Promise<AutomationOut> {
		return this.request<AutomationOut>(`/automations/${id}`);
	}

	async createAutomation(payload: GoalRequest): Promise<AutomationOut> {
		return this.request<AutomationOut>('/automations', {
			method: 'POST',
			body: JSON.stringify(payload)
		});
	}

	async deleteAutomation(id: string): Promise<{ message: string }> {
		return this.request<{ message: string }>(`/automations/${id}`, {
			method: 'DELETE'
		});
	}

	async runAutomation(id: string): Promise<RunOut> {
		return this.request<RunOut>(`/automations/${id}/run`, {
			method: 'POST'
		});
	}

	// Runs
	async getRun(runId: string): Promise<RunOut> {
		return this.request<RunOut>(`/runs/${runId}`);
	}

	async listAutomationRuns(automationId: string): Promise<RunOut[]> {
		return this.request<RunOut[]>(`/automations/${automationId}/runs`);
	}
}

export const api = new ApiClient();
