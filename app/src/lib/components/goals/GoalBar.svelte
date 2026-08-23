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
		placeholder = 'Enter natural language objective (e.g. "Daily at 8 AM, track RTX 4090 prices on Amazon and alert if below $1600")'
	}: Props = $props();

	let goalText = $state('');

	const templates = [
		'Daily at 9 AM, find cheapest PlayStation 5 in Nigeria and alert if price < 400000 NGN',
		'Weekly on Monday, extract remote Principal Go Engineer roles paying over $180k',
		'Every morning, find 2-bedroom apartments for rent in Lekki Phase 1 under 4,000,000 NGN',
		'Every 6 hours, monitor tech news mentions of "open source AI regulation"'
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
			class="absolute -inset-0.5 bg-gradient-to-r from-orbit-cyan via-orbit-violet to-orbit-emerald rounded-2xl opacity-30 group-focus-within:opacity-75 blur-sm transition duration-300"
		></div>

		<div class="relative bg-surface-900 border border-white/10 rounded-2xl p-2 shadow-2xl flex items-center gap-3">
			<div class="pl-3 text-orbit-cyan">
				<Sparkles size={20} class="animate-pulse" />
			</div>

			<input
				type="text"
				bind:value={goalText}
				{placeholder}
				disabled={loading}
				class="w-full bg-transparent text-slate-100 text-base placeholder-slate-500 focus:outline-none py-2 font-sans selection:bg-orbit-cyan/30"
			/>

			<div class="flex items-center gap-2 pr-1">
				<Button
					type="submit"
					variant="primary"
					size="md"
					{loading}
					disabled={!goalText.trim()}
					class="font-medium shrink-0"
				>
					<span>Interpret Goal</span>
					<ArrowRight size={16} />
				</Button>
			</div>
		</div>
	</form>

	<!-- Quick Template Starters -->
	<div class="flex items-center gap-2 flex-wrap text-xs text-slate-400">
		<span class="font-mono text-slate-500 uppercase tracking-wider text-[10px]">Example Missions:</span>
		{#each templates as tmpl}
			<button
				type="button"
				onclick={() => selectTemplate(tmpl)}
				class="px-2.5 py-1 rounded-md bg-surface-800/80 hover:bg-surface-700/80 text-slate-300 hover:text-orbit-cyan border border-white/5 transition-all text-left truncate max-w-xs hover:border-orbit-cyan/30"
			>
				{tmpl}
			</button>
		{/each}
	</div>
</div>
