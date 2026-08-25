<script lang="ts">
	import { GitBranch, Play, RefreshCw, PanelLeft, Plus } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onDeploy: () => void;
		onReset: () => void;
		onTogglePalette: () => void;
		paletteOpen: boolean;
		deploying?: boolean;
	}

	let { onDeploy, onReset, onTogglePalette, paletteOpen, deploying = false }: Props = $props();
</script>

<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
	<div class="flex items-center gap-3">
		{#if !paletteOpen}
			<button
				type="button"
				onclick={onTogglePalette}
				class="px-3 py-1.5 rounded-xl bg-surface-900 border border-white/10 text-xs font-mono text-slate-300 hover:text-white hover:border-orbit-cyan/50 transition-all flex items-center gap-2 shadow-lg"
				title="Open Adapter Library"
			>
				<PanelLeft size={14} class="text-orbit-cyan" />
				<span>Open Library</span>
			</button>
		{/if}

		<div>
			<h1 class="text-2xl font-bold text-slate-100 flex items-center gap-2 font-display">
				<GitBranch size={22} class="text-orbit-cyan" />
				<span>Pipeline Studio</span>
			</h1>
			<p class="text-xs text-slate-400 font-sans mt-0.5">
				Orchestrate document ingestion, LLM schema extraction, S3 storage, and notifications.
			</p>
		</div>
	</div>

	<div class="flex items-center gap-2.5">
		<Button variant="secondary" size="sm" onclick={onReset}>
			<RefreshCw size={13} />
			<span>Reset</span>
		</Button>
		<Button variant="primary" size="md" loading={deploying} onclick={onDeploy}>
			<Play size={14} />
			<span>Deploy Pipeline</span>
		</Button>
	</div>
</div>
