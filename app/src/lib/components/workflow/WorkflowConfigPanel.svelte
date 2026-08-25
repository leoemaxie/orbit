<script lang="ts">
	import { X, Check, Sliders, Activity, ShieldCheck } from '@lucide/svelte';
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
	<div class="bg-surface-900 border border-white/10 rounded-2xl p-5 space-y-4 shadow-2xl">
		<div class="flex items-center justify-between border-b border-white/10 pb-3">
			<div class="flex items-center gap-2">
				<Sliders size={16} class="text-orbit-cyan" />
				<h3 class="text-sm font-semibold text-white">{node.label}</h3>
				<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-800 text-slate-300 border border-white/10">
					{node.config.mode || 'both'}
				</span>
			</div>
			<button type="button" onclick={onClose} class="p-1 rounded text-slate-400 hover:text-white transition-colors">
				<X size={16} />
			</button>
		</div>

		<p class="text-xs text-slate-400 font-mono">{node.description}</p>

		<div class="space-y-3 font-mono text-xs">
			{#each Object.entries(configState) as [key, value]}
				{#if key !== 'mode'}
					<div class="space-y-1">
						<label for={key} class="text-[11px] uppercase text-slate-400 font-semibold">{key.replace(/_/g, ' ')}</label>
						{#if typeof value === 'boolean'}
							<div class="flex items-center gap-3 pt-1">
								<input type="checkbox" id={key} bind:checked={configState[key]} class="w-4 h-4 rounded bg-surface-800 border-white/20 text-orbit-cyan cursor-pointer" />
								<span class="text-slate-300">{configState[key] ? 'Enabled' : 'Disabled'}</span>
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
			<div class="p-2.5 rounded-lg text-xs font-mono border {testResult.success ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'}">
				{testResult.message}
			</div>
		{/if}

		<div class="pt-3 border-t border-white/10 flex items-center justify-between">
			<Button variant="secondary" size="sm" loading={testing} onclick={handleTestConnection}>
				<Activity size={13} />
				<span>Test Connection</span>
			</Button>
			<Button variant="primary" size="sm" onclick={() => onSave(configState)}>
				Save Settings
			</Button>
		</div>
	</div>
{/if}
