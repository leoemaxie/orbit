<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { ArrowLeft, Terminal, ShieldAlert, CheckCircle2, Clock, Globe, RefreshCw } from '@lucide/svelte';
	import { api } from '$lib/api/client';
	import type { RunOut } from '$lib/api/types';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import ProvenanceGraph from '$lib/components/provenance/ProvenanceGraph.svelte';
	import LogDrawer from '$lib/components/provenance/LogDrawer.svelte';
	import DataTable from '$lib/components/data/DataTable.svelte';

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
	<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
		<a
			href={run ? `/automations/${run.automation_id}` : '/automations'}
			class="inline-flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-orbit-cyan"
		>
			<ArrowLeft size={14} />
			<span>Back to Automation Mission</span>
		</a>

		<div class="flex items-center gap-2 self-end sm:self-auto">
			<Button variant="secondary" size="sm" onclick={loadRunDetails}>
				<RefreshCw size={13} class={loading ? 'animate-spin' : ''} />
				<span>Refresh</span>
			</Button>
			<Button variant="outline" size="sm" onclick={handleOpenAllLogs}>
				<Terminal size={13} />
				<span>Audit Logs</span>
			</Button>
		</div>
	</div>

	{#if loading && !run}
		<div class="text-center py-16 font-mono text-slate-400 text-sm">
			Loading run telemetry...
		</div>
	{:else if run}
		<!-- Run Telemetry Header -->
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 sm:p-5 space-y-4 shadow-2xl">
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-white/5 pb-4">
				<div>
					<div class="flex items-center gap-2 mb-1 flex-wrap">
						<span class="text-xs font-mono text-slate-400">RUN:</span>
						<code class="text-xs font-mono text-orbit-cyan break-all">{run.id}</code>
						<StatusBadge status={run.status} />
					</div>
					<div class="text-xs text-slate-400 font-mono">
						Started: {new Date(run.started_at).toLocaleString()}
						{#if run.finished_at}
							• Finished: {new Date(run.finished_at).toLocaleString()}
						{/if}
					</div>
				</div>

				<!-- Telemetry Counter Chips -->
				<div class="grid grid-cols-2 sm:flex sm:items-center gap-2 text-xs font-mono">
					<div class="px-3 py-1.5 rounded-lg bg-surface-800 border border-white/5 text-center sm:text-left">
						<span class="text-slate-500 text-[10px] block sm:inline">SOURCES:</span> <strong class="text-slate-200">{run.sources_found?.length || 0}</strong>
					</div>
					<div class="px-3 py-1.5 rounded-lg bg-surface-800 border border-white/5 text-center sm:text-left">
						<span class="text-slate-500 text-[10px] block sm:inline">PAGES:</span> <strong class="text-slate-200">{run.pages_retrieved?.length || 0}</strong>
					</div>
					<div class="px-3 py-1.5 rounded-lg bg-surface-800 border border-white/5 text-center sm:text-left">
						<span class="text-slate-500 text-[10px] block sm:inline">EXTRACTED:</span> <strong class="text-emerald-400">{run.extracted_count || 0}</strong>
					</div>
					<div class="px-3 py-1.5 rounded-lg bg-surface-800 border border-white/5 text-center sm:text-left">
						<span class="text-slate-500 text-[10px] block sm:inline">VALIDATED:</span> <strong class="text-orbit-cyan">{run.validated_count || 0}</strong>
					</div>
				</div>
			</div>

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
