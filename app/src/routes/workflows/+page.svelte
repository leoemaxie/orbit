<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import WorkflowHeader from '$lib/components/workflow/WorkflowHeader.svelte';
	import WorkflowPalette from '$lib/components/workflow/WorkflowPalette.svelte';
	import WorkflowCanvas from '$lib/components/workflow/WorkflowCanvas.svelte';
	import WorkflowConfigPanel from '$lib/components/workflow/WorkflowConfigPanel.svelte';
	import type { WorkflowNodeData, WorkflowEdge, NodeTemplate } from '$lib/components/workflow/types';

	const defaultTriggerNode: WorkflowNodeData[] = [
		{
			id: 'node_trigger_1',
			label: 'Schedule Trigger',
			category: 'trigger',
			iconName: 'Play',
			description: 'Cron schedule & webhook trigger',
			status: 'active',
			x: 40,
			y: 50,
			config: { frequency: 'daily', schedule_time: '08:00', timezone: 'UTC' }
		}
	];

	let nodes = $state<WorkflowNodeData[]>(JSON.parse(JSON.stringify(defaultTriggerNode)));
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

	function handleAddNode(template: NodeTemplate) {
		const newId = `node_${Date.now()}`;
		const lastNode = nodes[nodes.length - 1];
		const x = lastNode ? (lastNode.x + 260 > 620 ? 40 : lastNode.x + 260) : 40;
		const y = lastNode ? (lastNode.x + 260 > 620 ? lastNode.y + 170 : lastNode.y) : 50;
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
		onReset={() => {
			nodes = JSON.parse(JSON.stringify(defaultTriggerNode));
			selectedNode = null;
		}}
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
