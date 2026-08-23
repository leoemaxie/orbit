<script lang="ts">
	import { goto } from '$app/navigation';
	import { Layers, Play, Trash2, Search, ExternalLink, Globe, Clock, Plus } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';

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

	<!-- Automations Table / List -->
	<div class="border border-white/10 rounded-xl overflow-hidden bg-surface-900 shadow-2xl">
		<div class="overflow-x-auto">
			<table class="w-full text-left border-collapse font-sans text-xs">
				<thead class="bg-surface-850 border-b border-white/10 text-[11px] font-mono uppercase text-slate-400 tracking-wider">
					<tr>
						<th class="py-3 px-4">Status</th>
						<th class="py-3 px-4">Domain</th>
						<th class="py-3 px-4">Objective & Goal</th>
						<th class="py-3 px-4">Cadence</th>
						<th class="py-3 px-4">Created</th>
						<th class="py-3 px-4 text-right">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-white/5 font-mono">
					{#each filteredAutomations as auto}
						<tr class="hover:bg-surface-800/60 transition-colors">
							<td class="py-3 px-4">
								<StatusBadge status={auto.active ? 'success' : 'paused'} label={auto.active ? 'ACTIVE' : 'PAUSED'} />
							</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded text-[10px] uppercase bg-surface-800 text-orbit-violet border border-orbit-violet/30">
									{auto.plan?.domain || 'GENERAL'}
								</span>
							</td>
							<td class="py-3 px-4 max-w-md font-sans">
								<a href={`/automations/${auto.id}`} class="font-medium text-slate-100 hover:text-orbit-cyan block">
									{auto.plan?.objective || auto.raw_goal}
								</a>
								<span class="text-[11px] text-slate-400 font-mono line-clamp-1 mt-0.5">"{auto.raw_goal}"</span>
							</td>
							<td class="py-3 px-4 text-slate-300">
								<span class="uppercase">{auto.plan?.frequency}</span>
								{#if auto.plan?.schedule_time}
									<span class="text-slate-500 text-[11px] block">{auto.plan.schedule_time}</span>
								{/if}
							</td>
							<td class="py-3 px-4 text-slate-500 text-[11px]">
								{new Date(auto.created_at).toLocaleDateString()}
							</td>
							<td class="py-3 px-4 text-right space-x-2">
								<Button
									variant="primary"
									size="sm"
									onclick={() => handleRun(auto.id)}
									loading={orbitStore.runningAutomation && orbitStore.selectedAutomation?.id === auto.id}
								>
									<Play size={12} />
									<span>Run</span>
								</Button>
								<button
									onclick={() => handleDelete(auto.id)}
									class="p-1.5 text-slate-500 hover:text-rose-400 rounded hover:bg-rose-950/40 transition-colors"
									title="Delete automation"
								>
									<Trash2 size={14} />
								</button>
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan={6} class="py-12 text-center text-slate-500 font-mono">
								No matching automations found.
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
