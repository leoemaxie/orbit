export type NodeCategory = 'trigger' | 'discovery' | 'parsing' | 'extraction' | 'dossier' | 'storage' | 'notify';

export interface WorkflowNodeData {
	id: string;
	label: string;
	category: NodeCategory;
	iconName: string;
	description: string;
	status: 'active' | 'configured' | 'optional';
	x: number;
	y: number;
	config: Record<string, any>;
}

export interface WorkflowEdge {
	from: string;
	to: string;
}

export interface AdapterConfigField {
	key: string;
	label: string;
	type: 'text' | 'select' | 'boolean' | 'number';
	options?: string[];
	defaultVal: any;
	description: string;
}
