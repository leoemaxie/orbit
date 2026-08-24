<script lang="ts">
	import WorkflowNode from './WorkflowNode.svelte';
	import type { WorkflowNodeData, WorkflowEdge } from './types';

	interface Props {
		nodes: WorkflowNodeData[];
		edges: WorkflowEdge[];
		selectedNode: WorkflowNodeData | null;
		onSelectNode: (node: WorkflowNodeData) => void;
	}

	let { nodes, edges, selectedNode, onSelectNode }: Props = $props();
</script>

<div class="relative w-full min-h-[580px] bg-surface-950/80 border border-white/10 rounded-2xl p-6 overflow-x-auto overflow-y-hidden shadow-2xl backdrop-blur-md">
	<!-- Background Blueprint Grid Pattern -->
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none rounded-2xl"></div>

	<!-- Canvas Layout Grid -->
	<div class="relative z-10 flex items-center justify-between gap-8 min-w-[1020px] py-12">
		{#each nodes as node, idx}
			<div class="flex items-center gap-6">
				<!-- Node Component -->
				<WorkflowNode
					{node}
					selected={selectedNode?.id === node.id}
					onSelect={onSelectNode}
				/>

				<!-- n8n-style Animated Pulse Connection Line -->
				{#if idx < nodes.length - 1}
					<div class="relative w-12 flex items-center justify-center shrink-0">
						<div class="w-full h-0.5 bg-gradient-to-r from-white/20 via-orbit-cyan/60 to-white/20"></div>
						<div class="absolute w-2 h-2 rounded-full bg-orbit-cyan shadow-glow-cyan animate-ping"></div>
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>
