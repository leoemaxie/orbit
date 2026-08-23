<script lang="ts">
	import { ShieldAlert } from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
</script>

{#if !orbitStore.daemonConnected}
	<div class="bg-rose-950/80 border-b border-rose-600/30 px-4 sm:px-6 py-2.5 text-xs text-rose-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
		<div class="flex items-center gap-2">
			<ShieldAlert size={15} class="text-rose-400 shrink-0" />
			<span>Orbit Daemon unreachable. Make sure the Orbit core service is running.</span>
		</div>
		<button
			type="button"
			onclick={() => orbitStore.checkHealth()}
			class="px-2.5 py-1 rounded bg-rose-900 hover:bg-rose-800 text-rose-100 font-mono text-[11px] self-start sm:self-auto shrink-0 transition-colors"
		>
			Retry Connection
		</button>
	</div>
{/if}
