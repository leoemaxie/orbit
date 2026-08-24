<script lang="ts">
	import { Sparkles, ArrowRight } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onSubmit: (goal: string) => void;
		loading?: boolean;
		placeholder?: string;
	}

	let {
		onSubmit,
		loading = false,
		placeholder = 'e.g. Daily at 6 AM, monitor SaaS pricing changes across enterprise vendors and alert on drops above 10%'
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

<div class="w-full space-y-3">
	<form onsubmit={handleSubmit} class="relative group">
		<!-- Ambient glow border -->
		<div
			class="absolute -inset-px bg-gradient-to-r from-orbit-cyan via-orbit-violet to-orbit-emerald rounded-2xl opacity-20 group-focus-within:opacity-60 blur-sm transition-all duration-300 pointer-events-none"
		></div>

		<div class="relative bg-surface-900 border border-white/10 rounded-2xl px-4 py-3 shadow-2xl flex items-center gap-3">
			<Sparkles size={18} class="text-orbit-cyan shrink-0 opacity-70" />

			<input
				type="text"
				bind:value={goalText}
				{placeholder}
				disabled={loading}
				class="min-w-0 flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none font-sans"
			/>

			<Button
				type="submit"
				variant="primary"
				size="sm"
				{loading}
				disabled={!goalText.trim()}
				class="shrink-0 font-medium"
			>
				<span>Create Mission</span>
				<ArrowRight size={14} />
			</Button>
		</div>
	</form>

	<!-- Example missions grid -->
	<div class="space-y-2">
		<p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500 px-1">Example missions</p>
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
			{#each templates as tmpl}
				<button
					type="button"
					onclick={() => selectTemplate(tmpl)}
					class="text-left px-3 py-2.5 rounded-lg bg-surface-900 hover:bg-surface-800 border border-white/8 hover:border-orbit-cyan/30 text-xs text-slate-400 hover:text-slate-200 transition-all leading-relaxed"
				>
					{tmpl}
				</button>
			{/each}
		</div>
	</div>
</div>
