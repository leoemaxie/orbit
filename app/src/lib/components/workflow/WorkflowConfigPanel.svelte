<script lang="ts">
	import { X, Sliders, Activity, Save } from '@lucide/svelte';
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
	{@const effectiveType = node.adapterType || (node.id.includes('storage') || node.id.includes('database') || node.id.includes('slack') || node.id.includes('email') || node.id.includes('template') ? 'custom' : 'managed')}
	<aside class="w-80 bg-surface-900 border border-white/10 rounded-2xl p-4 flex flex-col gap-3 shadow-2xl shrink-0 max-h-[640px] h-fit">
		<!-- Header with Title & Mode -->
		<div class="flex items-center justify-between border-b border-white/10 pb-2.5">
			<div class="flex items-center gap-2 min-w-0">
				<Sliders size={14} class="text-orbit-cyan shrink-0" />
				<h3 class="text-xs font-bold text-white uppercase tracking-wider truncate font-mono">{node.label}</h3>
				<span class="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded border {effectiveType === 'managed'
					? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/20'
					: 'bg-cyan-950/40 text-cyan-300 border-cyan-500/20'}">
					{effectiveType}
				</span>
			</div>
			<button type="button" onclick={onClose} class="p-1 rounded text-slate-400 hover:text-white hover:bg-surface-800 transition-colors" title="Close inspector">
				<X size={14} />
			</button>
		</div>

		<p class="text-[11px] font-mono text-slate-400 leading-tight">{node.description}</p>

		<!-- Form Fields Compact Area -->
		<div class="overflow-y-auto max-h-[380px] space-y-2.5 font-mono text-xs pr-1 custom-scrollbar">
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

		<!-- Action Buttons Directly Beneath Fields -->
		<div class="pt-2.5 border-t border-white/10 flex items-center justify-between gap-2">
			<Button variant="secondary" size="sm" loading={testing} onclick={handleTestConnection}>
				<Activity size={12} />
				<span>Test Probe</span>
			</Button>
			<Button variant="primary" size="sm" onclick={() => onSave(configState)}>
				<Save size={12} />
				<span>Save Settings</span>
			</Button>
		</div>
	</aside>
{/if}
