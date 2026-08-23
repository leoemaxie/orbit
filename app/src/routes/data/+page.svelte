<script lang="ts">
	import { onMount } from 'svelte';
	import { Database, RefreshCw, Layers } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import { api } from '$lib/api/client';
	import type { ResultOut, RunOut } from '$lib/api/types';
	import DataTable from '$lib/components/data/DataTable.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	let allResults = $state<ResultOut[]>([]);
	let loading = $state(true);

	async function loadAllData() {
		loading = true;
		try {
			await orbitStore.loadAutomations();
			const results: ResultOut[] = [];

			// Fetch runs for all automations in parallel
			const promises = orbitStore.automations.map(async (auto) => {
				try {
					const runs = await api.listAutomationRuns(auto.id);
					for (const r of runs) {
						if (r.results && r.results.length > 0) {
							results.push(...r.results);
						}
					}
				} catch (e) {
					// continue
				}
			});

			await Promise.all(promises);
			allResults = results;
		} catch (err) {
			console.error('Failed to load global data warehouse:', err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadAllData();
	});
</script>

<div class="max-w-6xl mx-auto space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-slate-100 flex items-center gap-2 font-display">
				<Database size={22} class="text-orbit-cyan" />
				<span>Data Warehouse</span>
			</h1>
			<p class="text-xs text-slate-400 font-sans mt-1">
				Unified repository of verified records and anomalies extracted across all orbit missions.
			</p>
		</div>

		<Button variant="secondary" size="md" onclick={loadAllData} {loading} class="w-full sm:w-auto">
			<RefreshCw size={14} class={loading ? 'animate-spin' : ''} />
			<span>Refresh Warehouse</span>
		</Button>
	</div>

	<!-- Data Explorer Component -->
	<DataTable results={allResults} title="Global Telemetry Records" />
</div>
