<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import {
		Orbit,
		Radio,
		Layers,
		Database,
		Sparkles,
		Terminal,
		Activity,
		ShieldAlert,
		RefreshCw,
		Play,
		ExternalLink
	} from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import { API_BASE } from '$lib/api/client';
	import OrbitLogo from '$lib/components/ui/OrbitLogo.svelte';

	let { children } = $props();

	onMount(() => {
		orbitStore.checkHealth();
		orbitStore.loadAutomations();

		// Background polling for health status every 10 seconds
		const timer = setInterval(() => {
			orbitStore.checkHealth();
		}, 10000);

		return () => clearInterval(timer);
	});

	const navItems = [
		{ href: '/', label: 'Overview', icon: Radio },
		{ href: '/automations', label: 'Automation Fleet', icon: Layers },
		{ href: '/data', label: 'Data Warehouse', icon: Database }
	];
</script>

<div class="min-h-screen flex bg-void text-slate-100 font-sans">
	<!-- Left Navigation Sidebar -->
	<aside class="w-64 bg-surface-900 border-r border-white/10 flex flex-col justify-between shrink-0 z-20">
		<!-- Brand / Logo -->
		<div class="p-4 border-b border-white/10 flex items-center justify-between">
			<a href="/" class="group block">
				<OrbitLogo size="md" showWordmark={true} animated={true} class="group-hover:opacity-90 transition-opacity" />
			</a>
		</div>

		<!-- Navigation Links -->
		<nav class="p-3 space-y-1 flex-1">
			<div class="px-3 py-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-500">
				Operations Hub
			</div>

			{#each navItems as item}
				{@const active = page.url.pathname === item.href || (item.href !== '/' && page.url.pathname.startsWith(item.href))}
				<a
					href={item.href}
					class="flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all {active
						? 'bg-gradient-to-r from-orbit-cyan/15 to-transparent text-orbit-cyan border-l-2 border-orbit-cyan font-semibold'
						: 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'}"
				>
					<item.icon size={16} />
					<span>{item.label}</span>
				</a>
			{/each}
		</nav>

		<!-- Bottom Telemetry & Daemon Status -->
		<div class="p-4 border-t border-white/10 bg-surface-850 space-y-3">
			<div class="flex items-center justify-between">
				<span class="text-[11px] font-mono text-slate-400">Daemon Gateway</span>
				<span
					class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono border {orbitStore.daemonConnected
						? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30'
						: 'bg-rose-950/60 text-rose-400 border-rose-500/30'}"
				>
					<span class="w-1.5 h-1.5 rounded-full {orbitStore.daemonConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}"></span>
					{orbitStore.daemonConnected ? 'ONLINE' : 'OFFLINE'}
				</span>
			</div>

			{#if orbitStore.health}
				<div class="text-[10px] font-mono text-slate-500 space-y-0.5">
					<div>Env: {orbitStore.health.environment}</div>
					<div>Scheduler: {orbitStore.health.scheduler_enabled ? 'Active' : 'Disabled'}</div>
				</div>
			{/if}
		</div>
	</aside>

	<!-- Main Content Canvas -->
	<div class="flex-1 flex flex-col min-w-0 overflow-hidden">
		<!-- Top Bar -->
		<header class="h-14 bg-surface-900/80 backdrop-blur-md border-b border-white/10 px-6 flex items-center justify-between shrink-0 z-10">
			<div class="flex items-center gap-3 text-xs font-mono text-slate-400">
				<Activity size={14} class="text-orbit-cyan animate-pulse" />
				<span>Active Automations: <strong class="text-slate-100">{orbitStore.activeAutomationsCount}</strong></span>
			</div>

			<div class="flex items-center gap-3">
				<button
					onclick={() => orbitStore.loadAutomations()}
					class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors"
					title="Refresh Telemetry"
				>
					<RefreshCw size={14} class={orbitStore.loading ? 'animate-spin' : ''} />
				</button>
			</div>
		</header>

		<!-- Global Error Banner if Daemon Unreachable -->
		{#if !orbitStore.daemonConnected}
			<div class="bg-rose-950/80 border-b border-rose-600/30 px-6 py-2.5 text-xs text-rose-200 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<ShieldAlert size={15} class="text-rose-400" />
					<span>Orbit Daemon unreachable at <code class="font-mono bg-rose-900/50 px-1.5 py-0.5 rounded">{API_BASE}</code>. Make sure the Orbit core service is running.</span>
				</div>
				<button
					onclick={() => orbitStore.checkHealth()}
					class="px-2.5 py-1 rounded bg-rose-900 hover:bg-rose-800 text-rose-100 font-mono text-[11px]"
				>
					Retry Connection
				</button>
			</div>
		{/if}

		<!-- Page Viewport -->
		<main class="flex-1 overflow-y-auto p-6 md:p-8 space-y-8">
			{@render children()}
		</main>
	</div>
</div>
