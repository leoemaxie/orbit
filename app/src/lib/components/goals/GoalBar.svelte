<script lang="ts">
	import { Sparkles, ArrowRight, CornerDownLeft, Bot, Globe, Shield } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onSubmit: (goal: string) => void;
		loading?: boolean;
		placeholder?: string;
	}

	let {
		onSubmit,
		loading = false,
		placeholder = 'Enter natural language objective (e.g. "Daily at 6 AM, monitor pricing and inventory across enterprise cloud vendors")'
	}: Props = $props();

	let goalText = $state('');

	const templates = [
		'Daily at 6 AM, monitor pricing, SKU availability, and inventory changes across top 5 enterprise cloud hardware vendors',
		'Weekly on Monday, aggregate median tech compensation bands, level distributions, and hiring volume across Tier 1 fintechs',
		'Every 4 hours, scan regional energy regulatory portals for policy updates on renewable grid tariffs and alert on changes',
		'Daily, extract and structure AI research preprints mentioning sparse attention architectures with author affiliation schemas'
	];

	function handleSubmit(e?: Event) {
		e?.preventDefault();
		if (!goalText.trim() || loading) return;
		onSubmit(goalText.trim());
	}

	function selectTemplate(tmpl: string) {
		goalText = tmpl;
	}
</script>

<div class="w-full max-w-4xl mx-auto space-y-4">
	<form onsubmit={handleSubmit} class="relative group">
		<!-- Pulsing ambient border glow -->
		<div
			class="absolute -inset-0.5 bg-gradient-to-r from-orbit-cyan via-orbit-violet to-orbit-emerald rounded-2xl opacity-30 group-focus-within:opacity-75 blur-sm transition duration-300 pointer-events-none"
		></div>

		<div class="relative bg-surface-900 border border-white/10 rounded-2xl p-2 sm:p-2.5 shadow-2xl flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 overflow-hidden">
			<div class="hidden sm:flex pl-2 text-orbit-cyan shrink-0">
				<Sparkles size={20} class="animate-pulse" />
			</div>

			<input
				type="text"
				bind:value={goalText}
				{placeholder}
				disabled={loading}
				class="min-w-0 flex-1 bg-transparent text-slate-100 text-sm sm:text-base placeholder-slate-500 focus:outline-none px-2 sm:px-0 py-1.5 font-sans selection:bg-orbit-cyan/30"
			/>

			<div class="shrink-0 flex justify-end">
				<Button
					type="submit"
					variant="primary"
					size="md"
					{loading}
					disabled={!goalText.trim()}
					class="font-medium whitespace-nowrap w-full sm:w-auto"
				>
					<span>Interpret Goal</span>
					<ArrowRight size={16} />
				</Button>
			</div>
		</div>
	</form>

	<!-- High-Stake Mission Templates -->
	<div class="flex items-center gap-2 flex-wrap text-xs text-slate-400">
		<span class="font-mono text-slate-500 uppercase tracking-wider text-[10px]">Example Missions:</span>
		{#each templates as tmpl}
			<button
				type="button"
				onclick={() => selectTemplate(tmpl)}
				class="px-2.5 py-1 rounded-md bg-surface-800/80 hover:bg-surface-700/80 text-slate-300 hover:text-orbit-cyan border border-white/5 transition-all text-left truncate max-w-sm hover:border-orbit-cyan/30"
				title={tmpl}
			>
				{tmpl}
			</button>
		{/each}
	</div>
</div>
