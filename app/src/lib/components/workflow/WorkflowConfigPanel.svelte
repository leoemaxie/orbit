<script lang="ts">
	import { X, Sliders, Activity } from '@lucide/svelte';
	import { api } from '$lib/api/client';
	import Button from '$lib/components/ui/Button.svelte';
	import type { WorkflowNodeData } from './types';

	interface Props {
		node: WorkflowNodeData | null;
		onClose: () => void;
		onSave: (updatedConfig: Record<string, any>) => void;
	}

	let { node, onClose, onSave }: Props = $props();
	let configState = $state<Record<string, any>>({});
	let testing = $state(false);
	let testResult = $state<{ success: boolean; message: string } | null>(null);

	$effect(() => {
		if (node) {
			configState = { ...node.config };
			testResult = null;
		}
	});

	async function handleTestConnection() {
		if (!node) return;
		testing = true;
		testResult = null;
		try {
			const res = await api.testAdapterConnection(node.id, configState);
			testResult = res;
		} catch (e: any) {
			testResult = { success: false, message: e.message || 'Probe failed' };
		} finally {
			testing = false;
		}
	}
</script>

{#if node}
	<aside class="w-80 bg-surface-900 border border-white/10 rounded-2xl p-4 flex flex-col gap-4 shadow-2xl shrink-0 h-[640px]">
		<!-- Header -->
		<div class="flex items-center justify-between border-b border-white/10 pb-3">
			<div class="flex items-center gap-2 min-w-0">
				<Sliders size={15} class="text-orbit-cyan shrink-0" />
				<h3 class="text-xs font-bold text-white uppercase tracking-wider truncate font-mono">{node.label}</h3>
			</div>
			<button type="button" onclick={onClose} class="p-1 rounded text-slate-400 hover:text-white hover:bg-surface-800 transition-colors" title="Close inspector">
				<X size={15} />
			</button>
		</div>

		<div class="flex items-center justify-between gap-2">
			<span class="text-[10px] font-mono text-slate-400 truncate">{node.description}</span>
			<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-800 text-orbit-cyan border border-white/10 shrink-0">
				{node.config.mode || 'both'}
			</span>
		</div>

		<!-- Form Fields Scroll Area -->
		<div class="flex-1 overflow-y-auto space-y-3 font-mono text-xs pr-1 custom-scrollbar">
			{#each Object.entries(configState) as [key, value]}
				{#if key !== 'mode'}
					<div class="space-y-1">
						<label for={key} class="text-[10px] uppercase text-slate-400 font-semibold">{key.replace(/_/g, ' ')}</label>
						{#if typeof value === 'boolean'}
							<div class="flex items-center gap-3 pt-0.5">
								<input type="checkbox" id={key} bind:checked={configState[key]} class="w-4 h-4 rounded bg-surface-800 border-white/20 text-orbit-cyan cursor-pointer" />
								<span class="text-slate-300 text-xs">{configState[key] ? 'Enabled' : 'Disabled'}</span>
							</div>
						{:else}
							<input
								type={key.includes('key') || key.includes('secret') || key.includes('webhook') ? 'password' : 'text'}
								id={key}
								bind:value={configState[key]}
								class="w-full px-3 py-1.5 bg-surface-800 border border-white/10 rounded-lg text-slate-100 focus:outline-none focus:border-orbit-cyan/60"
							/>
						{/if}
					</div>
				{/if}
			{/each}
		</div>

		{#if testResult}
			<div class="p-2 rounded-lg text-[11px] font-mono border {testResult.success ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'}">
				{testResult.message}
			</div>
		{/if}

		<!-- Footer Action Buttons -->
		<div class="pt-3 border-t border-white/10 flex items-center justify-between gap-2">
			<Button variant="secondary" size="sm" loading={testing} onclick={handleTestConnection}>
				<Activity size={12} />
				<span>Test Probe</span>
			</Button>
			<Button variant="primary" size="sm" onclick={() => onSave(configState)}>
				Save Settings
			</Button>
		</div>
	</aside>
{/if}
