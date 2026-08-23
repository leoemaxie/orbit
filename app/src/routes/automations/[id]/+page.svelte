<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Layers, Play, Clock, ArrowLeft, Database, Search, Bell, History } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import { api } from '$lib/api/client';
	import type { AutomationOut, RunOut } from '$lib/api/types';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import PlanPreviewCard from '$lib/components/goals/PlanPreviewCard.svelte';

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
		<div class="space-y-4">
			<div class="flex items-center gap-2">
				<History size={18} class="text-orbit-cyan" />
				<h2 class="text-base font-semibold text-slate-100">Past Execution Runs</h2>
				<span class="text-xs font-mono px-2 py-0.5 rounded bg-surface-800 text-slate-400 border border-white/10">
					{runs.length} runs
				</span>
			</div>

			<div class="border border-white/10 rounded-xl overflow-hidden bg-surface-900 shadow-2xl">
				<div class="overflow-x-auto">
					<table class="w-full text-left border-collapse font-sans text-xs">
						<thead class="bg-surface-850 border-b border-white/10 text-[11px] font-mono uppercase text-slate-400 tracking-wider">
							<tr>
								<th class="py-3 px-4">Run Status</th>
								<th class="py-3 px-4">Started At</th>
								<th class="py-3 px-4">Sources Found</th>
								<th class="py-3 px-4">Pages Retrieved</th>
								<th class="py-3 px-4">Extracted Records</th>
								<th class="py-3 px-4">Condition Alert</th>
								<th class="py-3 px-4 text-right">Inspect</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-white/5 font-mono">
							{#each runs as r}
								<tr class="hover:bg-surface-800/60 transition-colors">
									<td class="py-3 px-4">
										<StatusBadge status={r.status} />
									</td>
									<td class="py-3 px-4 text-slate-300">
										{new Date(r.started_at).toLocaleString()}
									</td>
									<td class="py-3 px-4 text-slate-400">
										{r.sources_found?.length || 0}
									</td>
									<td class="py-3 px-4 text-slate-400">
										{r.pages_retrieved?.length || 0}
									</td>
									<td class="py-3 px-4 text-emerald-400 font-semibold">
										{r.extracted_count || 0}
									</td>
									<td class="py-3 px-4">
										{#if r.condition_matched === true}
											<span class="text-amber-400 text-[11px] font-bold">MATCHED</span>
										{:else if r.condition_matched === false}
											<span class="text-slate-500 text-[11px]">NO MATCH</span>
										{:else}
											<span class="text-slate-600">—</span>
										{/if}
									</td>
									<td class="py-3 px-4 text-right">
										<a
											href={`/runs/${r.id}`}
											class="text-xs font-mono text-orbit-cyan hover:underline"
										>
											View Telemetry →
										</a>
									</td>
								</tr>
							{:else}
								<tr>
									<td colspan={7} class="py-12 text-center text-slate-500 font-mono">
										No previous runs found for this automation.
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	{:else}
		<div class="text-center py-16 text-rose-400 font-mono text-sm">
			Automation not found.
		</div>
	{/if}
</div>
