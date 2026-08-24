<script lang="ts">
	import { goto } from '$app/navigation';
	import { Layers, ArrowRight, Plus } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import GoalBar from '$lib/components/goals/GoalBar.svelte';
	import PlanPreviewCard from '$lib/components/goals/PlanPreviewCard.svelte';
	import AutomationGridCard from '$lib/components/dashboard/AutomationGridCard.svelte';
	import type { AutomationOut } from '$lib/api/types';

	let previewAutomation = $state<AutomationOut | null>(null);
	let runningId = $state<string | null>(null);

	async function handleGoalSubmit(goal: string) {
		const created = await orbitStore.createGoal(goal);
		if (created) {
			previewAutomation = created;
		}
	}

	async function handleRunNow(automationId: string) {
		runningId = automationId;
		try {
			const run = await orbitStore.triggerRun(automationId);
			if (run) {
				goto(`/runs/${run.id}`);
			}
		} finally {
			runningId = null;
		}
	}
</script>

<div class="max-w-5xl mx-auto space-y-8 pb-12">
	<div class="space-y-1">
		<h1 class="text-xl font-semibold text-slate-100 tracking-tight">New Mission</h1>
		<p class="text-sm text-slate-400 hidden sm:block">Define a data extraction objective in plain language. Orbit will synthesize an execution plan and schedule it automatically.</p>
	</div>

	<GoalBar onSubmit={handleGoalSubmit} loading={orbitStore.interpretingGoal} />

	{#if previewAutomation}
		<div class="space-y-3 animate-in fade-in-50 slide-in-from-bottom-2 duration-300">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span class="w-1.5 h-1.5 rounded-full bg-orbit-cyan animate-pulse"></span>
					<span class="text-xs font-semibold text-orbit-cyan uppercase tracking-wider">Execution Plan Ready</span>
				</div>
				<button type="button" onclick={() => (previewAutomation = null)} class="text-xs text-slate-500 hover:text-slate-300 transition-colors">
					Dismiss
				</button>
			</div>
			<PlanPreviewCard
				automation={previewAutomation}
				onRunNow={handleRunNow}
				running={runningId === previewAutomation.id}
			/>
		</div>
	{/if}

	<div class="space-y-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2.5">
				<Layers size={16} class="text-orbit-cyan" />
				<h2 class="text-sm font-semibold text-slate-100">Active Fleet</h2>
				<span class="inline-flex items-center px-2 py-0.5 rounded-md bg-surface-800 border border-white/10 text-[11px] font-medium text-slate-400">
					{orbitStore.automations.length}
				</span>
			</div>
			<a href="/automations" class="text-xs font-medium text-slate-400 hover:text-orbit-cyan transition-colors flex items-center gap-1">
				<span>View all</span>
				<ArrowRight size={12} />
			</a>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
			{#each orbitStore.automations.slice(0, 6) as auto (auto.id)}
				<AutomationGridCard
					automation={auto}
					running={runningId === auto.id}
					onRun={handleRunNow}
				/>
			{:else}
				<div class="col-span-full border border-dashed border-white/10 rounded-xl p-8 text-center space-y-3">
					<div class="w-10 h-10 rounded-full bg-surface-800 flex items-center justify-center mx-auto">
						<Plus size={18} class="text-slate-500" />
					</div>
					<div>
						<p class="text-sm font-medium text-slate-300">No automations yet</p>
						<p class="text-xs text-slate-500 mt-1">Use the goal bar above to define your first data extraction mission.</p>
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>
