<script lang="ts">
	import { X, Sliders, Activity, Save, CheckCircle2 } from '@lucide/svelte';
	import { api } from '$lib/api/client';
	import Button from '$lib/components/ui/Button.svelte';
	import WorkflowConfigFields from './WorkflowConfigFields.svelte';
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
	let saveError = $state<string | null>(null);
	let saving = $state(false);
	let saved = $state(false);
	let currentTrackedId = $state<string | null>(null);

	$effect(() => {
		if (node && node.id !== currentTrackedId) {
			currentTrackedId = node.id;
			configState = { ...node.config };
			testResult = null;
			saveError = null;
			saving = false;
			saved = false;
		}
	});

	function handleFieldChange() {
		saved = false;
		saveError = null;
	}

	async function handleTestConnection() {
		if (!node) return;
		testing = true;
		testResult = null;
		try {
			const identifier = node.typeId || node.id || node.label;
			testResult = await api.testAdapterConnection(identifier, configState);
		} catch (e: any) {
			testResult = { success: false, message: e.message || 'Probe failed' };
		} finally {
			testing = false;
		}
	}

	async function handleSave() {
		if (!node || saving) return;
		saving = true;
		saved = false;
		saveError = null;
		try {
			await api.saveAdapterConfig(node.id, configState);
			onSave(configState);
			saved = true;
		} catch (e: any) {
			saveError = e.message || 'Failed to save settings';
		} finally {
			saving = false;
		}
	}
</script>

{#if node}
	{@const effectiveType = node.adapterType || (node.id.includes('storage') || node.id.includes('database') || node.id.includes('slack') || node.id.includes('webhook') || node.id.includes('template') ? 'custom' : node.id.includes('email') ? 'both' : 'managed')}
	<aside class="w-full lg:w-80 bg-surface-900 border border-white/10 rounded-2xl p-4 flex flex-col gap-3 shadow-2xl shrink-0 max-h-[640px] h-fit">
		<!-- Header -->
		<div class="flex items-center justify-between border-b border-white/10 pb-2.5">
			<div class="flex items-center gap-2 min-w-0">
				<Sliders size={14} class="text-orbit-cyan shrink-0" />
				<h3 class="text-xs font-bold text-white uppercase tracking-wider truncate font-mono">{node.label}</h3>
				<span class="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded border {effectiveType === 'managed'
					? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/20'
					: effectiveType === 'both'
					? 'bg-amber-950/40 text-amber-300 border-amber-500/20'
					: 'bg-cyan-950/40 text-cyan-300 border-cyan-500/20'}">
					{effectiveType}
				</span>
			</div>
			<button type="button" onclick={onClose} class="p-1 rounded text-slate-400 hover:text-white hover:bg-surface-800 transition-colors">
				<X size={14} />
			</button>
		</div>

		<p class="text-[11px] font-mono text-slate-400 leading-tight">{node.description}</p>

		<!-- Dynamic Config Form Fields -->
		<WorkflowConfigFields {configState} onChange={handleFieldChange} />

		{#if saveError || testResult || saved}
			<div class="p-2 rounded-lg text-[11px] font-mono border {saveError ? 'bg-rose-950/40 border-rose-500/30 text-rose-300' : saved ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : testResult?.success ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'}">
				{saveError || (saved ? 'Configuration saved and applied to canvas.' : testResult?.message)}
			</div>
		{/if}

		<!-- Action Buttons -->
		<div class="pt-2.5 border-t border-white/10 flex items-center justify-between gap-2">
			<Button variant="secondary" size="sm" loading={testing} onclick={handleTestConnection}>
				<Activity size={12} />
				<span>Test Probe</span>
			</Button>
			<Button variant={saved ? 'secondary' : 'primary'} size="sm" loading={saving} disabled={saving} onclick={handleSave}>
				<Save size={12} />
				<span>{saved ? 'Saved!' : 'Save Settings'}</span>
			</Button>
		</div>
	</aside>
{/if}
