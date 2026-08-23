<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { api } from '$lib/api/client';
	import type { RunOut } from '$lib/api/types';
	import ProvenanceGraph from '$lib/components/provenance/ProvenanceGraph.svelte';
	import LogDrawer from '$lib/components/provenance/LogDrawer.svelte';
	import DataTable from '$lib/components/data/DataTable.svelte';
	import RunHeader from '$lib/components/runs/RunHeader.svelte';
	import RunTelemetryStats from '$lib/components/runs/RunTelemetryStats.svelte';

	let run = $state<RunOut | null>(null);
	let loading = $state(true);
	let drawerOpen = $state(false);
	let selectedNode = $state<string | null>(null);

	const runId = $derived(page.params.id);

	async function loadRunDetails() {
		if (!runId) return;
		try {
			run = await api.getRun(runId);
		} catch (err) {
			console.error(err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadRunDetails();

		// If running, poll every 2 seconds until completed
		const interval = setInterval(() => {
			if (run?.status === 'running' || run?.status === 'pending') {
				loadRunDetails();
			}
		}, 2000);

		return () => clearInterval(interval);
	});

	function handleSelectNode(nodeId: string) {
		selectedNode = nodeId;
		drawerOpen = true;
	}

	function handleOpenAllLogs() {
		selectedNode = 'all';
		drawerOpen = true;
	}
</script>

<div class="max-w-6xl mx-auto space-y-8">
	<!-- Header Navigation -->
	<RunHeader
		automationId={run?.automation_id}
		{loading}
		onRefresh={loadRunDetails}
		onOpenLogs={handleOpenAllLogs}
	/>

	{#if loading && !run}
		<div class="text-center py-16 font-mono text-slate-400 text-sm">
			Loading run telemetry...
		</div>
	{:else if run}
		<!-- Run Telemetry Header Card -->
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 sm:p-5 space-y-4 shadow-2xl">
			<RunTelemetryStats {run} />

			<!-- Provenance DAG Visualizer -->
			<div class="space-y-2 pt-2">
				<div class="flex items-center justify-between text-xs font-mono text-slate-400">
					<span>EXECUTION PROVENANCE DAG</span>
					<span class="text-[11px] text-slate-500">Click any stage to inspect logs & raw data</span>
				</div>
				<ProvenanceGraph
					{run}
					onSelectNode={handleSelectNode}
					{selectedNode}
				/>
			</div>
		</div>

		<!-- Extracted Records Data Table -->
		<div class="space-y-3">
			<DataTable results={run.results || []} />
		</div>

		<!-- Log & Telemetry Drawer -->
		<LogDrawer
			open={drawerOpen}
			{run}
			activeNode={selectedNode}
			onClose={() => (drawerOpen = false)}
		/>
	{:else}
		<div class="text-center py-16 text-rose-400 font-mono text-sm">
			Run telemetry not found.
		</div>
	{/if}
</div>
