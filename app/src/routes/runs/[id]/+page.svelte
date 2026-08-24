<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { Terminal, Database, GitFork } from '@lucide/svelte';
	import { api } from '$lib/api/client';
	import type { RunOut } from '$lib/api/types';
	import ProvenanceGraph from '$lib/components/provenance/ProvenanceGraph.svelte';
	import LogDrawer from '$lib/components/provenance/LogDrawer.svelte';
	import DataTable from '$lib/components/data/DataTable.svelte';
	import RunHeader from '$lib/components/runs/RunHeader.svelte';
	import RunTelemetryStats from '$lib/components/runs/RunTelemetryStats.svelte';
	import LiveExecutionConsole from '$lib/components/runs/LiveExecutionConsole.svelte';
	import LivePipelineSteps from '$lib/components/runs/LivePipelineSteps.svelte';

	let run = $state<RunOut | null>(null);
	let loading = $state(true);
	let activeTab = $state<'live' | 'data' | 'dag'>('live');
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
		const interval = setInterval(() => {
			if (run?.status === 'running' || run?.status === 'pending' || run?.status === 'discovering' || run?.status === 'retrieving' || run?.status === 'extracting') {
				loadRunDetails();
			}
		}, 1500);
		return () => clearInterval(interval);
	});
</script>

<div class="max-w-6xl mx-auto space-y-6">
	<RunHeader
		automationId={run?.automation_id}
		{loading}
		onRefresh={loadRunDetails}
		onOpenLogs={() => { selectedNode = 'all'; drawerOpen = true; }}
	/>

	{#if loading && !run}
		<div class="text-center py-16 font-mono text-slate-400 text-sm animate-pulse">
			Connecting to Orbit live execution stream...
		</div>
	{:else if run}
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 sm:p-5 space-y-4 shadow-2xl">
			<RunTelemetryStats {run} />
			<LivePipelineSteps {run} />
		</div>

		<div class="flex items-center gap-2 border-b border-white/10 pb-2">
			<button
				type="button"
				onclick={() => (activeTab = 'live')}
				class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono transition-all {activeTab === 'live' ? 'bg-orbit-cyan/20 text-orbit-cyan border border-orbit-cyan/40 font-semibold' : 'text-slate-400 hover:text-slate-200'}"
			>
				<Terminal size={14} />
				<span>Live Build Log</span>
			</button>
			<button
				type="button"
				onclick={() => (activeTab = 'data')}
				class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono transition-all {activeTab === 'data' ? 'bg-orbit-cyan/20 text-orbit-cyan border border-orbit-cyan/40 font-semibold' : 'text-slate-400 hover:text-slate-200'}"
			>
				<Database size={14} />
				<span>Extracted Records ({run.results?.length || 0})</span>
			</button>
			<button
				type="button"
				onclick={() => (activeTab = 'dag')}
				class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono transition-all {activeTab === 'dag' ? 'bg-orbit-cyan/20 text-orbit-cyan border border-orbit-cyan/40 font-semibold' : 'text-slate-400 hover:text-slate-200'}"
			>
				<GitFork size={14} />
				<span>Provenance DAG</span>
			</button>
		</div>

		{#if activeTab === 'live'}
			<LiveExecutionConsole {run} />
		{:else if activeTab === 'data'}
			<DataTable results={run.results || []} />
		{:else if activeTab === 'dag'}
			<div class="bg-surface-900 border border-white/10 rounded-xl p-4 space-y-2">
				<ProvenanceGraph {run} onSelectNode={(id) => { selectedNode = id; drawerOpen = true; }} {selectedNode} />
			</div>
		{/if}

		<LogDrawer open={drawerOpen} {run} activeNode={selectedNode} onClose={() => (drawerOpen = false)} />
	{:else}
		<div class="text-center py-16 text-rose-400 font-mono text-sm">Run telemetry not found.</div>
	{/if}
</div>
