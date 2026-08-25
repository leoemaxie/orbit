<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import WorkflowHeader from '$lib/components/workflow/WorkflowHeader.svelte';
	import WorkflowPalette from '$lib/components/workflow/WorkflowPalette.svelte';
	import WorkflowCanvas from '$lib/components/workflow/WorkflowCanvas.svelte';
	import WorkflowConfigPanel from '$lib/components/workflow/WorkflowConfigPanel.svelte';
	import type { WorkflowNodeData, WorkflowEdge, NodeTemplate } from '$lib/components/workflow/types';

	const initialNodes: WorkflowNodeData[] = [
		{ id: 'node_1', label: 'Schedule Trigger', category: 'trigger', iconName: 'Play', description: 'Cron schedule & webhook trigger', status: 'active', x: 30, y: 50, config: { frequency: 'daily', schedule_time: '08:00' } },
		{ id: 'node_2', label: 'Source Discovery', category: 'discovery', iconName: 'Search', description: 'Multi-engine search & proxy retrieval', status: 'active', x: 290, y: 50, config: { search_depth: 2, max_sources: 8 } },
		{ id: 'node_3', label: 'Document & Table Parser', category: 'parsing', iconName: 'FileText', description: 'Document layout & table deconstruction', status: 'active', x: 550, y: 50, config: { layout_analysis: true, ocr_enabled: true } },
		{ id: 'node_4', label: 'LLM Schema Extraction', category: 'extraction', iconName: 'Database', description: 'Structured JSON record extraction', status: 'active', x: 550, y: 220, config: { temperature: 0.1, anomaly_detection: true } },
		{ id: 'node_5', label: 'PDF Report Generator', category: 'dossier', iconName: 'ShieldCheck', description: 'PDF summary with PII masking', status: 'active', x: 290, y: 220, config: { format: 'pdf', pii_redaction: true } },
		{ id: 'node_6', label: 'Amazon S3 Storage', category: 'storage', iconName: 'Cloud', description: 'S3 bucket archival & presigned download', status: 'active', x: 30, y: 220, config: { bucket_name: 'orbit-exports', region: 'us-east-1' } },
		{ id: 'node_7', label: 'Slack Notifications', category: 'notify', iconName: 'MessageSquare', description: 'Slack alert webhook with report links', status: 'active', x: 30, y: 390, config: { channel: '#orbit-alerts' } }
	];

	let nodes = $state<WorkflowNodeData[]>(JSON.parse(JSON.stringify(initialNodes)));
	let selectedNode = $state<WorkflowNodeData | null>(null);
	let paletteOpen = $state(true);
	let deploying = $state(false);

	const edges = $derived<WorkflowEdge[]>(
		nodes.slice(0, -1).map((node, i) => ({
			id: `edge_${node.id}_${nodes[i + 1].id}`,
			from: node.id,
			to: nodes[i + 1].id
		}))
	);

	onMount(async () => {
		try {
			const serverNodes = await api.getWorkflowTopology();
			if (serverNodes && serverNodes.length > 0) {
				nodes = serverNodes.map((sn, idx) => ({
					...sn,
					x: initialNodes[idx]?.x ?? 40 + (idx % 3) * 260,
					y: initialNodes[idx]?.y ?? 40 + Math.floor(idx / 3) * 160
				}));
			}
		} catch {}
	});

	function handleAddNode(template: NodeTemplate) {
		const newId = `node_${Date.now()}`;
		const lastNode = nodes[nodes.length - 1];
		const x = lastNode ? (lastNode.x + 260 > 600 ? 40 : lastNode.x + 260) : 40;
		const y = lastNode ? (lastNode.x + 260 > 600 ? lastNode.y + 170 : lastNode.y) : 40;
		nodes.push({ id: newId, label: template.label, category: template.category, iconName: template.iconName, description: template.description, status: 'active', x, y, config: { ...template.defaultConfig } });
	}

	function handleDropNewNode(template: NodeTemplate, x: number, y: number) {
		const newId = `node_${Date.now()}`;
		nodes.push({ id: newId, label: template.label, category: template.category, iconName: template.iconName, description: template.description, status: 'active', x, y, config: { ...template.defaultConfig } });
	}

	function handleUpdatePosition(id: string, x: number, y: number) {
		const node = nodes.find((n) => n.id === id);
		if (node) { node.x = x; node.y = y; }
	}

	function handleDeleteNode(id: string) {
		nodes = nodes.filter((n) => n.id !== id);
		if (selectedNode?.id === id) selectedNode = null;
	}

	async function handleDeploy() {
		deploying = true;
		try { await api.deployWorkflow(nodes); } catch {} finally { deploying = false; }
	}
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<WorkflowHeader
		onDeploy={handleDeploy}
		onReset={() => (nodes = JSON.parse(JSON.stringify(initialNodes)))}
		{deploying}
	/>

	<div class="flex flex-col lg:flex-row items-start gap-6">
		{#if paletteOpen}
			<WorkflowPalette onAddNode={handleAddNode} onClose={() => (paletteOpen = false)} />
		{/if}

		<div class="flex-1 w-full space-y-4 min-w-0">
			<WorkflowCanvas
				{nodes}
				{edges}
				{selectedNode}
				{paletteOpen}
				onTogglePalette={() => (paletteOpen = !paletteOpen)}
				onSelectNode={(n) => (selectedNode = n)}
				onDeleteNode={handleDeleteNode}
				onDropNewNode={handleDropNewNode}
				onUpdateNodePosition={handleUpdatePosition}
			/>

			{#if selectedNode}
				<WorkflowConfigPanel
					node={selectedNode}
					onClose={() => (selectedNode = null)}
					onSave={(cfg) => {
						const idx = nodes.findIndex((n) => n.id === selectedNode?.id);
						if (idx !== -1) { nodes[idx].config = cfg; selectedNode = { ...nodes[idx] }; }
					}}
				/>
			{/if}
		</div>
	</div>
</div>
