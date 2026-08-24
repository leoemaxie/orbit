<script lang="ts">
	import { GitBranch, Play, CheckCircle2, RefreshCw } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onDeploy: () => void;
		onReset: () => void;
		deploying?: boolean;
	}

	let { onDeploy, onReset, deploying = false }: Props = $props();
</script>

<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
	<div>
		<h1 class="text-2xl font-bold text-slate-100 flex items-center gap-2 font-display">
			<GitBranch size={22} class="text-orbit-cyan" />
			<span>Adapter Workflow Canvas</span>
		</h1>
		<p class="text-xs text-slate-400 font-sans mt-1">
			Visually orchestrate document parsers, normalizers, PII redactors, S3 object storage, and Slack communication sinks.
		</p>
	</div>

	<div class="flex items-center gap-3">
		<Button variant="secondary" size="sm" onclick={onReset}>
			<RefreshCw size={13} />
			<span>Reset Canvas</span>
		</Button>
		<Button variant="primary" size="md" loading={deploying} onclick={onDeploy}>
			<Play size={14} />
			<span>Deploy Workflow Pipeline</span>
		</Button>
	</div>
</div>
