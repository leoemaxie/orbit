<script lang="ts">
	import { ArrowLeft, Terminal, RefreshCw } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		automationId?: string;
		loading: boolean;
		onRefresh: () => void;
		onOpenLogs: () => void;
	}

	let { automationId, loading, onRefresh, onOpenLogs }: Props = $props();
</script>

<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
	<a
		href={automationId ? `/automations/${automationId}` : '/automations'}
		class="inline-flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-orbit-cyan"
	>
		<ArrowLeft size={14} />
		<span>Back to Automation Mission</span>
	</a>

	<div class="flex items-center gap-2 self-end sm:self-auto">
		<Button variant="secondary" size="sm" onclick={onRefresh}>
			<RefreshCw size={13} class={loading ? 'animate-spin' : ''} />
			<span>Refresh</span>
		</Button>
		<Button variant="outline" size="sm" onclick={onOpenLogs}>
			<Terminal size={13} />
			<span>Audit Logs</span>
		</Button>
	</div>
</div>
