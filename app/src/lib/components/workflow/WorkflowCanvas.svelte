<script lang="ts">
	import WorkflowNode from './WorkflowNode.svelte';
	import WorkflowConnections from './WorkflowConnections.svelte';
	import type { WorkflowNodeData, WorkflowEdge, NodeTemplate } from './types';

	interface Props {
		nodes: WorkflowNodeData[];
		edges: WorkflowEdge[];
		selectedNode: WorkflowNodeData | null;
		onSelectNode: (node: WorkflowNodeData) => void;
		onDeleteNode: (id: string) => void;
		onDropNewNode: (template: NodeTemplate, x: number, y: number) => void;
		onUpdateNodePosition: (id: string, x: number, y: number) => void;
	}

	let { nodes, edges, selectedNode, onSelectNode, onDeleteNode, onDropNewNode, onUpdateNodePosition }: Props = $props();

	let canvasEl: HTMLDivElement;
	let draggingNodeId = $state<string | null>(null);
	let dragOffset = $state({ x: 0, y: 0 });

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		if (!canvasEl) return;
		const raw = e.dataTransfer?.getData('application/json');
		if (!raw) return;
		try {
			const template: NodeTemplate = JSON.parse(raw);
			const rect = canvasEl.getBoundingClientRect();
			const x = Math.max(20, Math.min(rect.width - 240, e.clientX - rect.left - 100));
			const y = Math.max(20, Math.min(rect.height - 100, e.clientY - rect.top - 40));
			onDropNewNode(template, x, y);
		} catch {}
	}

	function handleDragNodeStart(e: MouseEvent, node: WorkflowNodeData) {
		draggingNodeId = node.id;
		dragOffset = { x: e.clientX - node.x, y: e.clientY - node.y };
		window.addEventListener('mousemove', handleMouseMove);
		window.addEventListener('mouseup', handleMouseUp);
	}

	function handleMouseMove(e: MouseEvent) {
		if (!draggingNodeId || !canvasEl) return;
		const rect = canvasEl.getBoundingClientRect();
		const newX = Math.max(10, Math.min(rect.width - 230, e.clientX - dragOffset.x));
		const newY = Math.max(10, Math.min(rect.height - 90, e.clientY - dragOffset.y));
		onUpdateNodePosition(draggingNodeId, newX, newY);
	}

	function handleMouseUp() {
		draggingNodeId = null;
		window.removeEventListener('mousemove', handleMouseMove);
		window.removeEventListener('mouseup', handleMouseUp);
	}
</script>

<div
	bind:this={canvasEl}
	ondragover={handleDragOver}
	ondrop={handleDrop}
	role="region"
	aria-label="Workflow Canvas"
	class="relative flex-1 min-h-[640px] h-[640px] bg-surface-950/90 border border-white/10 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md select-none"
>
	<!-- Blueprint Grid Backdrop -->
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

	<!-- SVG Curve Connections Layer -->
	<WorkflowConnections {nodes} {edges} />

	<!-- Interactive Placed Nodes -->
	{#each nodes as node (node.id)}
		<WorkflowNode
			{node}
			selected={selectedNode?.id === node.id}
			onSelect={onSelectNode}
			onDelete={onDeleteNode}
			onDragNodeStart={handleDragNodeStart}
		/>
	{/each}

	{#if nodes.length === 0}
		<div class="absolute inset-0 flex flex-col items-center justify-center text-slate-500 pointer-events-none">
			<p class="text-sm font-medium">Canvas is empty</p>
			<p class="text-xs font-mono text-slate-600 mt-1">Drag adapters from the sidebar to assemble your pipeline</p>
		</div>
	{/if}
</div>
