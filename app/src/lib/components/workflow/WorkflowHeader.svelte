<script lang="ts">
	import { GitBranch, Play, RefreshCw, CheckCircle2, RotateCw } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onDeploy: () => void;
		onReset: () => void;
		onSyncTopology?: () => void;
		deploying?: boolean;
		deployed?: boolean;
		syncing?: boolean;
	}

	let { onDeploy, onReset, onSyncTopology, deploying = false, deployed = false, syncing = false }: Props = $props();
</script>

<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
	<div>
		<h1 class="text-2xl font-bold text-slate-100 flex items-center gap-2 font-display">
			<GitBranch size={22} class="text-orbit-cyan" />
			<span>Pipeline Studio</span>
		</h1>
		<p class="text-xs text-slate-400 font-sans mt-0.5">
			Orchestrate source discovery, LLM schema extraction, databases, S3 storage, and notifications.
		</p>
	</div>

	<div class="flex items-center gap-2.5 flex-wrap sm:flex-nowrap">
		{#if onSyncTopology}
			<Button variant="secondary" size="sm" loading={syncing} onclick={onSyncTopology} title="Fetch live adapter configurations from backend">
				<RotateCw size={13} class="text-orbit-cyan" />
				<span>Sync Active Topology</span>
			</Button>
		{/if}

		<Button variant="secondary" size="sm" onclick={onReset} title="Reset to empty pipeline canvas">
			<RefreshCw size={13} />
			<span>Reset</span>
		</Button>

		<Button
			variant={deployed ? 'secondary' : 'primary'}
			size="md"
			loading={deploying}
			disabled={deploying}
			onclick={onDeploy}
			class={deployed ? 'border-emerald-500/40 text-emerald-300 bg-emerald-950/30' : ''}
		>
			{#if deployed}
				<CheckCircle2 size={14} class="text-emerald-400" />
				<span>Pipeline Deployed!</span>
			{:else}
				<Play size={14} />
				<span>Deploy Pipeline</span>
			{/if}
		</Button>
	</div>
</div>
