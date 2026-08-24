<script lang="ts">
	import { goto } from '$app/navigation';
	import { Layers, Search, Plus } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import AutomationTable from '$lib/components/automations/AutomationTable.svelte';

	let searchQuery = $state('');

	const filteredAutomations = $derived.by(() => {
		if (!searchQuery.trim()) return orbitStore.automations;
		const q = searchQuery.toLowerCase();
		return orbitStore.automations.filter(
			(a) =>
				a.raw_goal.toLowerCase().includes(q) ||
				a.plan.objective.toLowerCase().includes(q) ||
				a.plan.domain.toLowerCase().includes(q)
		);
	});

	async function handleRun(id: string) {
		const run = await orbitStore.triggerRun(id);
		if (run) {
			goto(`/runs/${run.id}`);
		}
	}

	async function handleDelete(id: string) {
		if (confirm('Are you sure you want to terminate and delete this automation?')) {
			await orbitStore.deleteAutomation(id);
		}
	}
</script>

<div class="max-w-6xl mx-auto space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-slate-100 flex items-center gap-2 font-display">
				<Layers size={22} class="text-orbit-cyan" />
				<span>Automation Fleet</span>
			</h1>
			<p class="text-xs text-slate-400 font-sans mt-1">
				Your active automated data pipelines. Monitor recurring data extraction schedules, inspect data schemas, and execute runs on demand.
			</p>
		</div>

		<a href="/">
			<Button variant="primary" size="md">
				<Plus size={16} />
				<span>New Mission</span>
			</Button>
		</a>
	</div>

	<!-- Filter & Search Bar -->
	<div class="flex items-center gap-3 bg-surface-900 border border-white/10 p-3 rounded-xl">
		<div class="relative flex-1">
			<Search size={14} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Search automations by goal, domain, or objective..."
				class="w-full pl-8 pr-3 py-1.5 bg-surface-800 border border-white/10 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-orbit-cyan/50 font-mono"
			/>
		</div>
	</div>

	<!-- Automations Table -->
	<AutomationTable
		automations={filteredAutomations}
		runningAutomationId={orbitStore.runningAutomation && orbitStore.selectedAutomation ? orbitStore.selectedAutomation.id : null}
		onRun={handleRun}
		onDelete={handleDelete}
	/>
</div>
