<script lang="ts">
	import { goto } from '$app/navigation';
	import { Layers, ArrowRight, Plus, Globe, CheckCircle2 } from '@lucide/svelte';
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

<div class="max-w-5xl mx-auto flex flex-col justify-between min-h-[calc(100dvh-8rem)] md:min-h-0 md:block md:space-y-12 pb-2 md:pb-16">
	<!-- Hero Canvas (Vertically centered on mobile like Gemini, standard flow on desktop) -->
	<section class="flex-1 flex flex-col justify-center space-y-4 sm:space-y-6 md:space-y-8 py-2 md:py-12">
		<!-- Heroic Overview Header (Strictly 2 lines, centered, no asymmetric gap) -->
		<div class="text-center space-y-2 md:space-y-3">
			<h1 class="text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-bold tracking-tight font-display text-center leading-tight">
				<span class="bg-gradient-to-r from-orbit-cyan via-sky-300 to-orbit-violet bg-clip-text text-transparent block">
					What web data operations
				</span>
				<span class="text-slate-100 block mt-0.5 sm:mt-1 md:mt-2">
					do you want to automate?
				</span>
			</h1>
			<p class="hidden md:block text-sm text-slate-400 max-w-2xl mx-auto font-sans leading-relaxed">
				Define your objective in plain English. Orbit autonomously handles web discovery, structured extraction, anomaly validation, condition alerts, and downstream workflows.
			</p>
		</div>

		<!-- AI Prompt & Quick Suggestions Canvas -->
		<GoalBar onSubmit={handleGoalSubmit} loading={orbitStore.interpretingGoal} />
	</section>

	<!-- Dynamic Plan Preview Modal / Card -->
	{#if previewAutomation}
		<div class="space-y-3 animate-in fade-in-50 slide-in-from-bottom-2 duration-300 my-2">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-orbit-cyan animate-pulse"></span>
					<span class="text-xs font-semibold text-orbit-cyan uppercase tracking-wider font-mono">Extraction Plan Ready</span>
				</div>
				<button type="button" onclick={() => (previewAutomation = null)} class="text-xs text-slate-500 hover:text-slate-300 transition-colors font-mono">
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

	<!-- Active Web Monitors Fleet Section (Anchored at bottom on single mobile screen, standard grid on desktop) -->
	<div class="space-y-2 sm:space-y-3 pt-2 shrink-0">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<Layers size={15} class="text-orbit-cyan" />
				<h2 class="text-xs sm:text-base font-bold text-slate-100 font-display">Active Web Monitors</h2>
				<span class="inline-flex items-center px-1.5 py-0.2 sm:px-2 sm:py-0.5 rounded-md bg-surface-800 border border-white/10 text-[10px] sm:text-[11px] font-mono font-medium text-slate-400">
					{orbitStore.automations.length}
				</span>
			</div>
			<a href="/automations" class="text-[11px] sm:text-xs font-medium text-slate-400 hover:text-orbit-cyan transition-colors flex items-center gap-1 font-mono">
				<span class="hidden sm:inline">View all monitors</span>
				<span class="inline sm:hidden">View all</span>
				<ArrowRight size={11} />
			</a>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 sm:gap-3">
			{#each orbitStore.automations.slice(0, 6) as auto (auto.id)}
				<AutomationGridCard
					automation={auto}
					running={runningId === auto.id}
					onRun={handleRunNow}
				/>
			{:else}
				<div class="col-span-full border border-dashed border-white/10 rounded-xl sm:rounded-2xl p-3 sm:p-8 text-center space-y-1.5 sm:space-y-3 bg-surface-900/40">
					<div class="w-7 h-7 sm:w-11 sm:h-11 rounded-full bg-surface-800 border border-white/5 flex items-center justify-center mx-auto text-orbit-cyan">
						<Globe size={14} class="sm:hidden" />
						<Globe size={20} class="hidden sm:block" />
					</div>
					<div>
						<p class="text-xs sm:text-sm font-semibold text-slate-200">No active web monitors yet</p>
						<p class="text-[10px] sm:text-xs text-slate-500 mt-0.5 max-w-sm mx-auto">
							Type a data goal above or click a suggestion pill to start collecting web data hands-off.
						</p>
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>
