<script lang="ts">
	import { onMount } from 'svelte';
	import { Database, RefreshCw, Layers, Bot, Target, Calendar, ArrowUpRight, CheckCircle2, ShieldAlert, Filter, Globe, Sparkles } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import { api } from '$lib/api/client';
	import type { AutomationOut, ResultOut, RunOut } from '$lib/api/types';
	import DataTable from '$lib/components/data/DataTable.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface MissionData {
		automation: AutomationOut;
		results: ResultOut[];
		validCount: number;
		anomalyCount: number;
		totalCount: number;
		lastRunAt: string | null;
	}

	let missionsData = $state<MissionData[]>([]);
	let selectedMissionId = $state<string>('all');
	let loading = $state(true);

	// Global aggregated statistics
	const totalRecords = $derived.by(() => missionsData.reduce((acc, m) => acc + m.totalCount, 0));
	const totalValid = $derived.by(() => missionsData.reduce((acc, m) => acc + m.validCount, 0));
	const totalAnomalies = $derived.by(() => missionsData.reduce((acc, m) => acc + m.anomalyCount, 0));

	// Active filtered missions
	const visibleMissions = $derived.by(() => {
		if (selectedMissionId === 'all') {
			return missionsData;
		}
		return missionsData.filter((m) => m.automation.id === selectedMissionId);
	});

	async function loadWarehouseData() {
		loading = true;
		try {
			await orbitStore.loadAutomations();
			const missions: MissionData[] = [];

			const promises = orbitStore.automations.map(async (auto) => {
				try {
					const runs = await api.listAutomationRuns(auto.id);
					const autoResults: ResultOut[] = [];
					let lastRunTime: string | null = null;

					if (runs.length > 0) {
						lastRunTime = runs[0].started_at || null;
					}

					for (const r of runs) {
						if (r.results && r.results.length > 0) {
							autoResults.push(...r.results);
						}
					}

					const valid = autoResults.filter((r) => r.valid).length;
					const anomalies = autoResults.length - valid;

					missions.push({
						automation: auto,
						results: autoResults,
						validCount: valid,
						anomalyCount: anomalies,
						totalCount: autoResults.length,
						lastRunAt: lastRunTime
					});
				} catch (e) {
					console.error(`Failed to load runs for automation ${auto.id}:`, e);
				}
			});

			await Promise.all(promises);
			missionsData = missions;
		} catch (err) {
			console.error('Failed to load global data warehouse:', err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadWarehouseData();
	});
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<!-- Warehouse Header -->
	<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-slate-100 flex items-center gap-2.5 font-display tracking-tight">
				<Database size={24} class="text-orbit-cyan" />
				<span>Data Warehouse</span>
			</h1>
			<p class="text-xs text-slate-400 font-sans mt-1">
				Mission-segregated data repository of validated entities, schema tables, and anomalies.
			</p>
		</div>

		<Button variant="secondary" size="md" onclick={loadWarehouseData} {loading} class="w-full sm:w-auto">
			<RefreshCw size={14} class={loading ? 'animate-spin' : ''} />
			<span>Refresh Warehouse</span>
		</Button>
	</div>

	<!-- Global Warehouse Metrics -->
	<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
			<span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Missions Tracked</span>
			<div class="text-2xl font-bold font-mono text-slate-100 mt-2">{missionsData.length}</div>
		</div>
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
			<span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Total Records</span>
			<div class="text-2xl font-bold font-mono text-orbit-cyan mt-2">{totalRecords}</div>
		</div>
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
			<span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Verified Valid</span>
			<div class="text-2xl font-bold font-mono text-emerald-400 mt-2">{totalValid}</div>
		</div>
		<div class="bg-surface-900 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
			<span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Anomalies Detected</span>
			<div class="text-2xl font-bold font-mono text-rose-400 mt-2">{totalAnomalies}</div>
		</div>
	</div>

	<!-- Mission Selector Tabs -->
	<div class="bg-surface-900 border border-white/10 p-2 rounded-xl flex items-center gap-2 overflow-x-auto">
		<div class="flex items-center gap-1.5 text-xs text-slate-400 px-2 shrink-0 font-mono">
			<Filter size={13} class="text-orbit-cyan" />
			<span>Filter Mission:</span>
		</div>

		<button
			type="button"
			onclick={() => (selectedMissionId = 'all')}
			class="px-3 py-1.5 rounded-lg text-xs font-mono transition-colors shrink-0 flex items-center gap-1.5 {selectedMissionId === 'all' ? 'bg-orbit-cyan/20 text-orbit-cyan border border-orbit-cyan/40 font-medium' : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'}"
		>
			<Layers size={13} />
			<span>All Missions</span>
			<span class="px-1.5 py-0.2 text-[10px] rounded bg-white/10 text-slate-300 font-mono">{missionsData.length}</span>
		</button>

		{#each missionsData as m}
			<button
				type="button"
				onclick={() => (selectedMissionId = m.automation.id)}
				class="px-3 py-1.5 rounded-lg text-xs font-mono transition-colors shrink-0 flex items-center gap-1.5 max-w-xs truncate {selectedMissionId === m.automation.id ? 'bg-orbit-cyan/20 text-orbit-cyan border border-orbit-cyan/40 font-medium' : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'}"
				title={m.automation.raw_goal}
			>
				<Target size={13} />
				<span class="truncate">{m.automation.plan?.objective || m.automation.raw_goal}</span>
				<span class="px-1.5 py-0.2 text-[10px] rounded bg-white/10 text-slate-300 font-mono">{m.totalCount}</span>
			</button>
		{/each}
	</div>

	<!-- Mission Segregated Content Section -->
	{#if loading && missionsData.length === 0}
		<div class="bg-surface-900 border border-white/10 rounded-xl p-12 text-center text-slate-400 font-mono text-xs flex flex-col items-center gap-3">
			<RefreshCw size={24} class="animate-spin text-orbit-cyan" />
			<span>Indexing data warehouse and segregating schema tables...</span>
		</div>
	{:else if visibleMissions.length === 0}
		<div class="bg-surface-900 border border-white/10 rounded-xl p-12 text-center text-slate-400 font-mono text-xs">
			No data records found in the warehouse for the selected view.
		</div>
	{:else}
		<div class="space-y-8">
			{#each visibleMissions as mission}
				<div class="bg-surface-900 border border-white/10 rounded-xl p-5 space-y-4">
					<!-- Mission Metadata Banner -->
					<div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 pb-4 border-b border-white/5">
						<div class="space-y-1">
							<div class="flex items-center gap-2 flex-wrap">
								<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-orbit-cyan/10 text-orbit-cyan border border-orbit-cyan/30 uppercase tracking-wider">
									Entity: {mission.automation.plan?.extraction_schema?.entity_name || 'item'}
								</span>
								{#if mission.automation.plan?.domain}
									<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-950/60 text-purple-300 border border-purple-500/30 uppercase tracking-wider">
										{mission.automation.plan.domain}
									</span>
								{/if}
								{#if mission.automation.plan?.frequency}
									<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-800 text-slate-400 border border-white/10 flex items-center gap-1">
										<Calendar size={10} />
										<span>{mission.automation.plan.frequency}</span>
									</span>
								{/if}
							</div>

							<h2 class="text-lg font-bold text-slate-100 font-display">
								{mission.automation.plan?.objective || mission.automation.raw_goal}
							</h2>
							<p class="text-xs text-slate-400 font-mono line-clamp-1">
								Goal: {mission.automation.raw_goal}
							</p>
						</div>

						<!-- Quick Actions & Stats -->
						<div class="flex items-center gap-3 self-end lg:self-auto shrink-0">
							<div class="flex items-center gap-2 font-mono text-xs">
								<span class="flex items-center gap-1 text-emerald-400 bg-emerald-950/40 px-2 py-1 rounded border border-emerald-500/20">
									<CheckCircle2 size={12} /> {mission.validCount} valid
								</span>
								{#if mission.anomalyCount > 0}
									<span class="flex items-center gap-1 text-rose-400 bg-rose-950/40 px-2 py-1 rounded border border-rose-500/20">
										<ShieldAlert size={12} /> {mission.anomalyCount} anomalies
									</span>
								{/if}
							</div>

							<a
								href="/automations/{mission.automation.id}"
								class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-mono bg-surface-800 hover:bg-surface-700 text-slate-200 border border-white/10 transition-colors"
							>
								<span>Automation</span>
								<ArrowUpRight size={12} />
							</a>
						</div>
					</div>

					<!-- Schema Fields Badge Strip -->
					{#if mission.automation.plan?.extraction_schema?.fields?.length}
						<div class="flex items-center gap-2 flex-wrap text-xs font-mono text-slate-400">
							<span class="text-[11px] text-slate-500">Schema Fields:</span>
							{#each mission.automation.plan.extraction_schema.fields as field}
								<span class="px-2 py-0.5 rounded text-[11px] bg-surface-800 border border-white/5 text-slate-300">
									{field.name} <span class="text-slate-500 text-[10px]">({field.type}{field.required ? ' *' : ''})</span>
								</span>
							{/each}
						</div>
					{/if}

					<!-- Mission-Specific Table -->
					<DataTable results={mission.results} title={`${mission.automation.plan?.extraction_schema?.entity_name || 'Item'} Records`} />
				</div>
			{/each}
		</div>
	{/if}
</div>
