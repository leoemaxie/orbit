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

<div class="max-w-5xl mx-auto space-y-8 sm:space-y-12 pb-16">
	<!-- Heroic Overview Header (Gemini-Inspired Dominant Gradient Layout) -->
	<div class="text-left sm:text-center space-y-3 pt-6 sm:pt-12 md:pt-16">
		<h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight font-display leading-[1.14]">
			<span class="bg-gradient-to-r from-orbit-cyan via-sky-300 to-orbit-violet bg-clip-text text-transparent block">
				What web data operations
			</span>
			<span class="text-slate-100 block mt-1 sm:mt-2">
				do you want to automate?
			</span>
		</h1>
		<p class="hidden sm:block text-xs sm:text-sm text-slate-400 max-w-2xl sm:mx-auto font-sans leading-relaxed">
			Define your objective in plain English. Orbit autonomously handles web discovery, structured extraction, anomaly validation, condition alerts, and downstream workflows.
		</p>
	</div>

	<!-- AI Prompt & Quick Suggestions Canvas -->
	<GoalBar onSubmit={handleGoalSubmit} loading={orbitStore.interpretingGoal} />

	<!-- Dynamic Plan Preview Modal / Card -->
	{#if previewAutomation}
		<div class="space-y-3 animate-in fade-in-50 slide-in-from-bottom-2 duration-300">
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

	<!-- Active Web Monitors Fleet Grid -->
	<div class="space-y-4 pt-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2.5">
				<Layers size={16} class="text-orbit-cyan" />
				<h2 class="text-base font-bold text-slate-100 font-display">Active Web Monitors</h2>
				<span class="inline-flex items-center px-2 py-0.5 rounded-md bg-surface-800 border border-white/10 text-[11px] font-mono font-medium text-slate-400">
					{orbitStore.automations.length}
				</span>
			</div>
			<a href="/automations" class="text-xs font-medium text-slate-400 hover:text-orbit-cyan transition-colors flex items-center gap-1 font-mono">
				<span>View all monitors</span>
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
				<div class="col-span-full border border-dashed border-white/10 rounded-2xl p-6 sm:p-10 text-center space-y-3 bg-surface-900/40">
					<div class="w-12 h-12 rounded-full bg-surface-800 border border-white/5 flex items-center justify-center mx-auto text-orbit-cyan">
						<Globe size={22} />
					</div>
					<div>
						<p class="text-sm font-semibold text-slate-200">No active web monitors yet</p>
						<p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
							Type a data goal above or click a suggestion pill to start collecting web data hands-off.
						</p>
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>
