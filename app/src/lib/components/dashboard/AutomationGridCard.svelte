<script lang="ts">
	import { Play, ArrowRight } from '@lucide/svelte';
	import type { AutomationOut } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		automation: AutomationOut;
		running?: boolean;
		onRun: (id: string) => void;
	}

	let { automation, running = false, onRun }: Props = $props();
</script>

<Card class="flex flex-col justify-between space-y-4 hover:border-orbit-cyan/40">
	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-surface-800 text-orbit-violet border border-orbit-violet/30">
				{automation.plan?.domain || 'GENERAL'}
			</span>
			<StatusBadge
				status={automation.active ? 'success' : 'paused'}
				label={automation.active ? 'ACTIVE' : 'PAUSED'}
			/>
		</div>
		<h3 class="text-sm font-medium text-slate-100 line-clamp-2">
			{automation.plan?.objective || automation.raw_goal}
		</h3>
		<p class="text-xs text-slate-400 font-mono line-clamp-1">
			Cadence: {automation.plan?.frequency}
		</p>
	</div>

	<div class="flex items-center justify-between border-t border-white/5 pt-3">
		<a
			href={`/automations/${automation.id}`}
			class="text-xs text-slate-400 hover:text-white font-mono flex items-center gap-1"
		>
			<span>Inspector</span>
			<ArrowRight size={11} />
		</a>

		<Button
			variant="primary"
			size="sm"
			loading={running}
			onclick={() => onRun(automation.id)}
		>
			<Play size={12} />
			<span>Run</span>
		</Button>
	</div>
</Card>
