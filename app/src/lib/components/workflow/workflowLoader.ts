import { api } from '$lib/api/client';
import type { WorkflowNodeData, NodeTemplate } from './types';

export const defaultTriggerNode: WorkflowNodeData[] = [
	{
		id: 'node_trigger_1',
		label: 'Schedule Trigger',
		category: 'trigger',
		adapterType: 'managed',
		iconName: 'Play',
		description: 'Cron schedule & webhook trigger',
		status: 'configured',
		x: 40,
		y: 50,
		config: { frequency: 'daily', schedule_time: '08:00', timezone: 'UTC' }
	}
];

export function persistLocalNodes(currentNodes: WorkflowNodeData[]): void {
	if (typeof window !== 'undefined' && window.localStorage) {
		try {
			window.localStorage.setItem('orbit_workflow_canvas_nodes', JSON.stringify(currentNodes));
		} catch {}
	}
}

export function getLocalNodes(): WorkflowNodeData[] | null {
	if (typeof window !== 'undefined' && window.localStorage) {
		const saved = window.localStorage.getItem('orbit_workflow_canvas_nodes');
		if (saved) {
			try {
				const parsed = JSON.parse(saved);
				if (Array.isArray(parsed) && parsed.length > 0) return parsed;
			} catch {}
		}
	}
	return null;
}

export function clearLocalNodes(): void {
	if (typeof window !== 'undefined' && window.localStorage) {
		window.localStorage.removeItem('orbit_workflow_canvas_nodes');
	}
}

export function createNodeFromTemplate(template: NodeTemplate, x: number, y: number): WorkflowNodeData {
	return {
		id: `node_${Date.now()}`,
		label: template.label,
		category: template.category,
		adapterType: template.adapterType,
		iconName: template.iconName,
		description: template.description,
		status: 'active',
		x,
		y,
		config: { ...template.defaultConfig }
	};
}

export function calculateNextPosition(nodes: WorkflowNodeData[]): { x: number; y: number } {
	const lastNode = nodes[nodes.length - 1];
	const x = lastNode ? (lastNode.x + 260 > 620 ? 40 : lastNode.x + 260) : 40;
	const y = lastNode ? (lastNode.x + 260 > 620 ? lastNode.y + 170 : lastNode.y) : 50;
	return { x, y };
}

export async function fetchInitialWorkflowNodes(): Promise<WorkflowNodeData[]> {
	const pipeline = await api.getPipeline();
	if (Array.isArray(pipeline) && pipeline.length > 0) {
		persistLocalNodes(pipeline);
		return pipeline;
	}

	const local = getLocalNodes();
	if (local) return local;

	const topology = await api.getWorkflowTopology();
	if (Array.isArray(topology) && topology.length > 0) {
		const activeAdapters = topology.filter(
			(t) => t.status === 'active' || (t.config && Object.values(t.config).some((v) => Boolean(v)))
		);
		const targetList = activeAdapters.length > 0 ? activeAdapters : topology.slice(0, 4);

		let currentX = 40;
		let currentY = 50;
		const mappedNodes: WorkflowNodeData[] = targetList.map((t, i) => {
			const node: WorkflowNodeData = {
				id: `node_${t.id}_${Date.now()}_${i}`,
				label: t.label,
				category: t.category,
				adapterType: t.mode === 'managed' ? 'managed' : 'custom',
				iconName: t.iconName || 'Database',
				description: t.description,
				status: t.status === 'active' ? 'configured' : 'active',
				x: currentX,
				y: currentY,
				config: { ...t.config }
			};
			if (currentX + 260 > 680) {
				currentX = 40;
				currentY += 170;
			} else {
				currentX += 260;
			}
			return node;
		});

		if (mappedNodes.length > 0) {
			persistLocalNodes(mappedNodes);
			return mappedNodes;
		}
	}

	return JSON.parse(JSON.stringify(defaultTriggerNode));
}
