<script lang="ts">
	import { onMount } from 'svelte';
	import { CheckCircle2, X } from '@lucide/svelte';
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
			adapterType: 'managed',
			iconName: 'Play',
			description: 'Cron schedule & webhook trigger',
			status: 'configured',
			x: 40,
			y: 50,
			config: { frequency: 'daily', schedule_time: '08:00', timezone: 'UTC' }
		}
	];

	let nodes = $state<WorkflowNodeData[]>(JSON.parse(JSON.stringify(defaultTriggerNode)));
	let selectedNode = $state<WorkflowNodeData | null>(null);
	let paletteOpen = $state(true);
	let deploying = $state(false);
	let deployed = $state(false);
	let deployMessage = $state<string | null>(null);

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
		nodes.push({
			id: newId,
			label: template.label,
			category: template.category,
			adapterType: template.adapterType,
			iconName: template.iconName,
			description: template.description,
			status: 'active',
			x,
			y,
			config: { ...template.defaultConfig }
		});
	}

	function handleDropNewNode(template: NodeTemplate, x: number, y: number) {
		const newId = `node_${Date.now()}`;
		nodes.push({
			id: newId,
			label: template.label,
			category: template.category,
			adapterType: template.adapterType,
			iconName: template.iconName,
			description: template.description,
			status: 'active',
			x,
			y,
			config: { ...template.defaultConfig }
		});
	}

	function handleUpdatePosition(id: string, x: number, y: number) {
		const node = nodes.find((n) => n.id === id);
		if (node) {
			node.x = x;
			node.y = y;
		}
	}

	function handleDeleteNode(id: string) {
		nodes = nodes.filter((n) => n.id !== id);
		if (selectedNode?.id === id) selectedNode = null;
	}

	async function handleDeploy() {
		deploying = true;
		deployMessage = null;
		try {
			const res = await api.deployWorkflow(nodes);
			nodes = nodes.map((n) => ({ ...n, status: 'configured' }));
			if (selectedNode) {
				selectedNode = { ...selectedNode, status: 'configured' };
			}
			deployMessage = res.message || `Pipeline successfully deployed with ${nodes.length} active stages.`;
			deployed = true;
			setTimeout(() => {
				deployed = false;
			}, 4000);
		} catch (e: any) {
			deployMessage = `Deployment warning: ${e.message || 'Check connection'}`;
		} finally {
			deploying = false;
		}
	}
</script>

<div class="max-w-7xl mx-auto space-y-5">
	<WorkflowHeader
		onDeploy={handleDeploy}
		onReset={() => {
			nodes = JSON.parse(JSON.stringify(defaultTriggerNode));
			selectedNode = null;
			deployMessage = null;
		}}
		{deploying}
		{deployed}
	/>

	{#if deployMessage}
		<div class="p-3 rounded-xl border bg-emerald-950/40 border-emerald-500/30 text-emerald-300 flex items-center justify-between text-xs font-mono animate-in fade-in duration-200">
			<div class="flex items-center gap-2">
				<CheckCircle2 size={15} class="text-emerald-400 shrink-0" />
				<span>{deployMessage}</span>
			</div>
			<button
				type="button"
				onclick={() => (deployMessage = null)}
				class="text-slate-400 hover:text-white transition-colors"
				title="Dismiss"
			>
				<X size={14} />
			</button>
		</div>
	{/if}

	<div class="flex flex-col lg:flex-row items-start gap-4">
		{#if paletteOpen}
			<WorkflowPalette onAddNode={handleAddNode} onClose={() => (paletteOpen = false)} />
		{/if}

		<div class="flex-1 w-full min-w-0">
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
		</div>

		{#if selectedNode}
			<WorkflowConfigPanel
				node={selectedNode}
				onClose={() => (selectedNode = null)}
				onSave={(cfg) => {
					const idx = nodes.findIndex((n) => n.id === selectedNode?.id);
					if (idx !== -1) {
						nodes[idx].config = { ...cfg };
						nodes[idx].status = 'configured';
						selectedNode = { ...nodes[idx] };
					}
				}}
			/>
		{/if}
	</div>
</div>
