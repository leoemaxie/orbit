<script lang="ts">
	import { X, Sliders, Activity, Save, CheckCircle2 } from '@lucide/svelte';
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
	let saveError = $state<string | null>(null);
	let saving = $state(false);
	let saved = $state(false);

	let currentTrackedId = $state<string | null>(null);

	$effect(() => {
		if (node) {
			if (node.id !== currentTrackedId) {
				currentTrackedId = node.id;
				configState = { ...node.config };
				testResult = null;
				saveError = null;
				saving = false;
				saved = false;
			}
		} else {
			currentTrackedId = null;
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
			const res = await api.testAdapterConnection(node.id, configState);
			testResult = res;
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
			console.warn('Adapter config save warning:', e);
			saveError = e.message || 'Failed to save settings';
		} finally {
			saving = false;
		}
	}
</script>

{#if node}
	{@const effectiveType = node.adapterType || (node.id.includes('storage') || node.id.includes('database') || node.id.includes('slack') || node.id.includes('email') || node.id.includes('webhook') || node.id.includes('template') ? 'custom' : 'managed')}
	<aside class="w-80 bg-surface-900 border border-white/10 rounded-2xl p-4 flex flex-col gap-3 shadow-2xl shrink-0 max-h-[640px] h-fit">
		<!-- Header with Title & Mode -->
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
								<input type="checkbox" id={key} bind:checked={configState[key]} onchange={handleFieldChange} class="w-4 h-4 rounded bg-surface-800 border-white/20 text-orbit-cyan cursor-pointer" />
								<span class="text-slate-300 text-xs">{configState[key] ? 'Enabled' : 'Disabled'}</span>
							</div>
						{:else if typeof value === 'number'}
							<input
								type="number"
								id={key}
								bind:value={configState[key]}
								oninput={handleFieldChange}
								class="w-full px-3 py-1.5 bg-surface-800 border border-white/10 rounded-lg text-slate-100 focus:outline-none focus:border-orbit-cyan/60"
							/>
						{:else}
							<input
								type={!key.includes('url') && (key.includes('key') || key.includes('secret') || key.includes('password') || key.includes('token')) ? 'password' : 'text'}
								id={key}
								bind:value={configState[key]}
								oninput={handleFieldChange}
								placeholder={key.includes('url') ? 'https://...' : ''}
								class="w-full px-3 py-1.5 bg-surface-800 border border-white/10 rounded-lg text-slate-100 focus:outline-none focus:border-orbit-cyan/60"
							/>
						{/if}
					</div>
				{/if}
			{/each}
		</div>

		{#if saveError}
			<div class="p-2 rounded-lg text-[11px] font-mono border bg-rose-950/40 border-rose-500/30 text-rose-300">
				{saveError}
			</div>
		{:else if saved}
			<div class="p-2 rounded-lg text-[11px] font-mono border bg-emerald-950/40 border-emerald-500/30 text-emerald-300 flex items-center gap-1.5 animate-in fade-in duration-200">
				<CheckCircle2 size={13} />
				<span>Configuration saved and applied to canvas.</span>
			</div>
		{:else if testResult}
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
			<Button
				variant={saved ? 'secondary' : 'primary'}
				size="sm"
				loading={saving}
				disabled={saving}
				onclick={handleSave}
				class={saved ? 'border-emerald-500/40 text-emerald-300 bg-emerald-950/30' : ''}
			>
				{#if saved}
					<CheckCircle2 size={12} class="text-emerald-400" />
					<span>Saved!</span>
				{:else}
					<Save size={12} />
					<span>Save Settings</span>
				{/if}
			</Button>
		</div>
	</aside>
{/if}
