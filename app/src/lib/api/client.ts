import { PUBLIC_API_URL } from '$env/static/public';
import type { AutomationListOut, AutomationOut, GoalRequest, HealthStatus, RunOut } from './types';

export class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string = PUBLIC_API_URL || 'http://localhost:8000/api/v1') {
		this.baseUrl = baseUrl.replace(/\/+$/, '');
	}

	private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
		const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
		const url = `${this.baseUrl}${cleanEndpoint}`;
		const headers: HeadersInit = { 'Content-Type': 'application/json', Accept: 'application/json', ...options.headers };

		const response = await fetch(url, { ...options, headers });
		if (!response.ok) {
			let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
			try {
				const errorJson = await response.json();
				if (errorJson.detail) {
					errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
				}
			} catch {}
			throw new Error(errorMessage);
		}
		const text = await response.text();
		return text ? JSON.parse(text) : ({} as T);
	}

	async getHealth(): Promise<HealthStatus> { return this.request<HealthStatus>('/health'); }
	async listAutomations(): Promise<AutomationListOut> { return this.request<AutomationListOut>('/automations'); }
	async getAutomation(id: string): Promise<AutomationOut> { return this.request<AutomationOut>(`/automations/${id}`); }
	async createAutomation(payload: GoalRequest): Promise<AutomationOut> {
		return this.request<AutomationOut>('/automations', { method: 'POST', body: JSON.stringify(payload) });
	}
	async deleteAutomation(id: string): Promise<{ message: string }> {
		return this.request<{ message: string }>(`/automations/${id}`, { method: 'DELETE' });
	}
	async runAutomation(id: string): Promise<RunOut> {
		return this.request<RunOut>(`/automations/${id}/run`, { method: 'POST' });
	}
	async retryRun(runId: string): Promise<RunOut> {
		return this.request<RunOut>(`/runs/${runId}/retry`, { method: 'POST' });
	}
	async getRun(runId: string): Promise<RunOut> { return this.request<RunOut>(`/runs/${runId}`); }
	getRunStreamUrl(runId: string): string {
		return `${this.baseUrl}/runs/${runId}/stream`;
	}
	streamRun(runId: string, onUpdate: (run: RunOut) => void, onError?: (err: any) => void): () => void {
		const url = this.getRunStreamUrl(runId);
		const eventSource = new EventSource(url);

		const handleMessage = (e: MessageEvent) => {
			try {
				const data = JSON.parse(e.data);
				onUpdate(data);
			} catch (err) {
				console.error('Failed to parse SSE payload:', err);
			}
		};

		eventSource.addEventListener('snapshot', handleMessage);
		eventSource.addEventListener('update', handleMessage);
		eventSource.addEventListener('complete', (e) => {
			handleMessage(e);
			eventSource.close();
		});

		eventSource.onerror = (err) => {
			if (onError) onError(err);
		};

		return () => {
			eventSource.close();
		};
	}
	async listAutomationRuns(automationId: string): Promise<RunOut[]> {
		return this.request<RunOut[]>(`/automations/${automationId}/runs`);
	}
	async getWorkflowTopology(): Promise<any[]> { return this.request<any[]>('/workflows/topology'); }
	async getPipeline(): Promise<any[]> { return this.request<any[]>('/workflows/pipeline'); }
	async deployWorkflow(nodes: any[]): Promise<{ status: string; message: string }> {
		return this.request<{ status: string; message: string }>('/workflows/deploy', {
			method: 'POST',
			body: JSON.stringify({ nodes })
		});
	}
	async testAdapterConnection(adapterId: string, config: Record<string, any>): Promise<{ success: boolean; message: string }> {
		return this.request<{ success: boolean; message: string }>('/workflows/test-connection', {
			method: 'POST',
			body: JSON.stringify({ adapter_id: adapterId, config })
		});
	}
	async saveAdapterConfig(adapterId: string, config: Record<string, any>): Promise<{ status: string; message: string }> {
		return this.request<{ status: string; message: string }>(`/workflows/adapters/${adapterId}/config`, {
			method: 'POST',
			body: JSON.stringify({ config })
		});
	}
}

export const api = new ApiClient();
