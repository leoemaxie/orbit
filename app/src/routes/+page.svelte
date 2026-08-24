<script lang="ts">
	import { goto } from '$app/navigation';
	import { Layers, ArrowRight } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import GoalBar from '$lib/components/goals/GoalBar.svelte';
	import PlanPreviewCard from '$lib/components/goals/PlanPreviewCard.svelte';
	import HeroSection from '$lib/components/dashboard/HeroSection.svelte';
	import AutomationGridCard from '$lib/components/dashboard/AutomationGridCard.svelte';
	import type { AutomationOut } from '$lib/api/types';

	let previewAutomation = $state<AutomationOut | null>(null);

	async function handleGoalSubmit(goal: string) {
		const created = await orbitStore.createGoal(goal);
		if (created) {
			previewAutomation = created;
		}
	}

	async function handleRunNow(automationId: string) {
		const run = await orbitStore.triggerRun(automationId);
		if (run) {
			goto(`/runs/${run.id}`);
		}
	}
</script>

<div class="max-w-5xl mx-auto space-y-12 pb-12">
	<!-- Hero Section -->
	<HeroSection />

	<!-- Goal Omnibar -->
	<GoalBar
		onSubmit={handleGoalSubmit}
		loading={orbitStore.interpretingGoal}
	/>

	<!-- Two-Step Plan Preview Studio (if an automation was just synthesized) -->
	{#if previewAutomation}
		<div class="space-y-3 animate-in fade-in-50 duration-300">
			<div class="flex items-center justify-between">
				<span class="text-xs font-mono text-orbit-cyan uppercase tracking-wider font-semibold">
					✦ Synthesized Execution Plan Ready
				</span>
				<button
					type="button"
					onclick={() => (previewAutomation = null)}
					class="text-xs text-slate-500 hover:text-slate-300 font-mono"
				>
					Dismiss Preview
				</button>
			</div>
			<PlanPreviewCard
				automation={previewAutomation}
				onRunNow={handleRunNow}
				running={orbitStore.runningAutomation}
			/>
		</div>
	{/if}

	<!-- Active Automations Fleet Overview -->
	<div class="space-y-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<Layers size={18} class="text-orbit-cyan" />
				<h2 class="text-base font-semibold text-slate-100">Automation Fleet</h2>
				<span class="text-xs font-mono px-2 py-0.5 rounded bg-surface-800 text-slate-400 border border-white/10">
					{orbitStore.automations.length} missions
				</span>
			</div>
			<a
				href="/automations"
				class="text-xs font-mono text-orbit-cyan hover:underline flex items-center gap-1"
			>
				<span>View All</span>
				<ArrowRight size={13} />
			</a>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each orbitStore.automations.slice(0, 6) as auto}
				<AutomationGridCard
					automation={auto}
					running={orbitStore.runningAutomation && orbitStore.selectedAutomation?.id === auto.id}
					onRun={handleRunNow}
				/>
			{:else}
				<div class="col-span-full text-center py-12 bg-surface-900 border border-white/10 rounded-xl space-y-2">
					<p class="text-sm text-slate-400">No active automations in orbit.</p>
					<p class="text-xs text-slate-500 font-mono">Use the command bar above to synthesize your first mission.</p>
				</div>
			{/each}
		</div>
	</div>
</div>
