<script lang="ts">
	import { X, Check, Sliders, ShieldCheck } from '@lucide/svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import type { WorkflowNodeData } from './types';

	interface Props {
		node: WorkflowNodeData | null;
		onClose: () => void;
		onSave: (updatedConfig: Record<string, any>) => void;
	}

	let { node, onClose, onSave }: Props = $props();
	let configState = $state<Record<string, any>>({});
	let savedNotice = $state(false);

	$effect(() => {
		if (node) {
			configState = { ...node.config };
		}
	});

	function handleSave() {
		onSave(configState);
		savedNotice = true;
		setTimeout(() => (savedNotice = false), 2000);
	}
</script>

{#if node}
	<div class="bg-surface-900 border border-white/10 rounded-2xl p-5 space-y-4 shadow-2xl">
		<div class="flex items-center justify-between border-b border-white/10 pb-3">
			<div class="flex items-center gap-2">
				<Sliders size={16} class="text-orbit-cyan" />
				<h3 class="text-sm font-semibold text-white">{node.label} Configuration</h3>
			</div>
			<button type="button" onclick={onClose} class="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors">
				<X size={16} />
			</button>
		</div>

		<p class="text-xs text-slate-400 font-mono">{node.description}</p>

		<div class="space-y-3 font-mono text-xs">
			{#each Object.entries(configState) as [key, value]}
				<div class="space-y-1">
					<label for={key} class="text-[11px] uppercase text-slate-400 font-semibold">{key.replace(/_/g, ' ')}</label>
					{#if typeof value === 'boolean'}
						<div class="flex items-center gap-3 pt-1">
							<input
								type="checkbox"
								id={key}
								bind:checked={configState[key]}
								class="w-4 h-4 rounded bg-surface-800 border-white/20 text-orbit-cyan focus:ring-0 cursor-pointer"
							/>
							<span class="text-slate-300">{configState[key] ? 'Enabled' : 'Disabled'}</span>
						</div>
					{:else}
						<input
							type="text"
							id={key}
							bind:value={configState[key]}
							class="w-full px-3 py-1.5 bg-surface-800 border border-white/10 rounded-lg text-slate-100 focus:outline-none focus:border-orbit-cyan/60"
						/>
					{/if}
				</div>
			{/each}
		</div>

		<div class="pt-3 border-t border-white/10 flex items-center justify-between">
			<span class="text-[11px] font-mono text-emerald-400 flex items-center gap-1 {savedNotice ? 'opacity-100' : 'opacity-0'} transition-opacity">
				<Check size={13} />
				<span>Configuration saved</span>
			</span>
			<Button variant="primary" size="sm" onclick={handleSave}>
				Save Adapter Settings
			</Button>
		</div>
	</div>
{/if}
