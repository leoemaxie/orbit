<script lang="ts">
	import { goto } from '$app/navigation';
	import { Sparkles, Radio, Layers, Play, ArrowRight, ShieldCheck, Clock } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import GoalBar from '$lib/components/goals/GoalBar.svelte';
	import PlanPreviewCard from '$lib/components/goals/PlanPreviewCard.svelte';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import OrbitLogo from '$lib/components/ui/OrbitLogo.svelte';
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

<div class="max-w-6xl mx-auto space-y-10">
	<!-- Hero Section -->
	<div class="text-center space-y-4 pt-4 flex flex-col items-center">
		<OrbitLogo size="lg" showWordmark={false} animated={true} class="mb-1" />
		<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orbit-cyan/10 border border-orbit-cyan/30 text-orbit-cyan text-xs font-mono">
			<Sparkles size={13} class="animate-pulse" />
			<span>Set the goal. Walk away.</span>
		</div>
		<h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
			Autonomous Web Data Operations
		</h1>
		<p class="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
			Specify extraction objectives in natural language. Orbit discovers web sources, bypasses dynamic barriers, extracts structured records, and runs on schedule with complete provenance.
		</p>
	</div>

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
				<Card class="flex flex-col justify-between space-y-4 hover:border-orbit-cyan/40">
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-surface-800 text-orbit-violet border border-orbit-violet/30">
								{auto.plan?.domain || 'GENERAL'}
							</span>
							<StatusBadge
								status={auto.active ? 'success' : 'paused'}
								label={auto.active ? 'ACTIVE' : 'PAUSED'}
							/>
						</div>
						<h3 class="text-sm font-medium text-slate-100 line-clamp-2">
							{auto.plan?.objective || auto.raw_goal}
						</h3>
						<p class="text-xs text-slate-400 font-mono line-clamp-1">
							Cadence: {auto.plan?.frequency}
						</p>
					</div>

					<div class="flex items-center justify-between border-t border-white/5 pt-3">
						<a
							href={`/automations/${auto.id}`}
							class="text-xs text-slate-400 hover:text-white font-mono flex items-center gap-1"
						>
							<span>Inspector</span>
							<ArrowRight size={11} />
						</a>

						<Button
							variant="primary"
							size="sm"
							loading={orbitStore.runningAutomation && orbitStore.selectedAutomation?.id === auto.id}
							onclick={() => handleRunNow(auto.id)}
						>
							<Play size={12} />
							<span>Run</span>
						</Button>
					</div>
				</Card>
			{:else}
				<div class="col-span-full text-center py-12 bg-surface-900 border border-white/10 rounded-xl space-y-2">
					<p class="text-sm text-slate-400">No active automations in orbit.</p>
					<p class="text-xs text-slate-500 font-mono">Use the command bar above to synthesize your first mission.</p>
				</div>
			{/each}
		</div>
	</div>
</div>
