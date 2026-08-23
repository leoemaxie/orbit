<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { ArrowLeft } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import { api } from '$lib/api/client';
	import type { AutomationOut, RunOut } from '$lib/api/types';
	import PlanPreviewCard from '$lib/components/goals/PlanPreviewCard.svelte';
	import RunsHistoryTable from '$lib/components/automations/RunsHistoryTable.svelte';

	let automation = $state<AutomationOut | null>(null);
	let runs = $state<RunOut[]>([]);
	let loading = $state(true);

	const autoId = $derived(page.params.id);

	onMount(async () => {
		if (autoId) {
			try {
				automation = await api.getAutomation(autoId);
				runs = await api.listAutomationRuns(autoId);
			} catch (err) {
				console.error(err);
			} finally {
				loading = false;
			}
		}
	});

	async function handleRunNow() {
		if (!autoId) return;
		const run = await orbitStore.triggerRun(autoId);
		if (run) {
			goto(`/runs/${run.id}`);
		}
	}
</script>

<div class="max-w-6xl mx-auto space-y-8">
	<!-- Back Button -->
	<a href="/automations" class="inline-flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-orbit-cyan">
		<ArrowLeft size={14} />
		<span>Back to Automation Fleet</span>
	</a>

	{#if loading}
		<div class="text-center py-16 font-mono text-slate-400 text-sm">
			Loading automation details...
		</div>
	{:else if automation}
		<!-- Automation Plan View -->
		<PlanPreviewCard
			{automation}
			onRunNow={handleRunNow}
			running={orbitStore.runningAutomation}
		/>

		<!-- Execution History -->
		<RunsHistoryTable {runs} />
	{:else}
		<div class="text-center py-16 text-rose-400 font-mono text-sm">
			Automation not found.
		</div>
	{/if}
</div>
