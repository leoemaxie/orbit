export type NodeCategory =
	| 'trigger'
	| 'discovery'
	| 'parsing'
	| 'extraction'
	| 'dossier'
	| 'compliance'
	| 'storage'
	| 'notify';

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
	id: string;
	from: string;
	to: string;
}

export interface NodeTemplate {
	typeId: string;
	label: string;
	category: NodeCategory;
	iconName: string;
	description: string;
	defaultConfig: Record<string, any>;
}
