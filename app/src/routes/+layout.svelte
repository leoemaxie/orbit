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
		ExternalLink,
		Menu,
		X
	} from '@lucide/svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import { API_BASE } from '$lib/api/client';
	import OrbitLogo from '$lib/components/ui/OrbitLogo.svelte';

	let { children } = $props();
	let mobileMenuOpen = $state(false);

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

	function closeMobileMenu() {
		mobileMenuOpen = false;
	}
</script>

<div class="min-h-screen flex flex-col md:flex-row bg-void text-slate-100 font-sans">
	<!-- Mobile Header Bar (Visible on < md) -->
	<header class="md:hidden h-14 bg-surface-900 border-b border-white/10 px-4 flex items-center justify-between shrink-0 z-30 sticky top-0 backdrop-blur-md">
		<a href="/" onclick={closeMobileMenu}>
			<OrbitLogo size="sm" showWordmark={true} animated={true} />
		</a>

		<div class="flex items-center gap-2">
			<span
				class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono border {orbitStore.daemonConnected
					? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30'
					: 'bg-rose-950/60 text-rose-400 border-rose-500/30'}"
			>
				<span class="w-1.5 h-1.5 rounded-full {orbitStore.daemonConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}"></span>
				{orbitStore.daemonConnected ? 'ONLINE' : 'OFFLINE'}
			</span>

			<button
				type="button"
				onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
				class="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors"
				aria-label="Toggle navigation menu"
			>
				{#if mobileMenuOpen}
					<X size={20} />
				{:else}
					<Menu size={20} />
				{/if}
			</button>
		</div>
	</header>

	<!-- Mobile Drawer Navigation Overlay -->
	{#if mobileMenuOpen}
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden"
			onclick={closeMobileMenu}
		></div>

		<aside
			class="fixed top-0 left-0 bottom-0 w-72 bg-surface-900 border-r border-white/10 z-50 flex flex-col justify-between p-4 animate-in slide-in-from-left duration-200 md:hidden"
		>
			<div class="space-y-6">
				<!-- Brand Header in Mobile Drawer -->
				<div class="flex items-center justify-between pb-4 border-b border-white/10">
					<a href="/" onclick={closeMobileMenu}>
						<OrbitLogo size="md" showWordmark={true} animated={true} />
					</a>
					<button
						onclick={closeMobileMenu}
						class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800"
					>
						<X size={18} />
					</button>
				</div>

				<!-- Nav Links -->
				<nav class="space-y-1.5">
					<div class="px-3 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-500">
						Operations Hub
					</div>

					{#each navItems as item}
						{@const active = page.url.pathname === item.href || (item.href !== '/' && page.url.pathname.startsWith(item.href))}
						<a
							href={item.href}
							onclick={closeMobileMenu}
							class="flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all {active
								? 'bg-gradient-to-r from-orbit-cyan/15 to-transparent text-orbit-cyan border-l-2 border-orbit-cyan font-semibold'
								: 'text-slate-300 hover:text-white hover:bg-surface-800'}"
						>
							<div class="flex items-center gap-3">
								<item.icon size={17} class={active ? 'text-orbit-cyan' : 'text-slate-400'} />
								<span>{item.label}</span>
							</div>
							{#if active}
								<span class="w-1.5 h-1.5 rounded-full bg-orbit-cyan"></span>
							{/if}
						</a>
					{/each}
				</nav>
			</div>

			<!-- Mobile Bottom Daemon Status -->
			<div class="p-3 rounded-xl bg-surface-850 border border-white/10 space-y-2">
				<div class="flex items-center justify-between text-xs font-mono">
					<span class="text-slate-400">Daemon</span>
					<span class="font-semibold text-xs {orbitStore.daemonConnected ? 'text-emerald-400' : 'text-rose-400'}">
						{orbitStore.daemonConnected ? 'CONNECTED' : 'UNREACHABLE'}
					</span>
				</div>
				{#if orbitStore.health}
					<div class="text-[10px] font-mono text-slate-500">
						Env: {orbitStore.health.environment} • Scheduler: {orbitStore.health.scheduler_enabled ? 'Active' : 'Disabled'}
					</div>
				{/if}
			</div>
		</aside>
	{/if}

	<!-- Desktop Navigation Sidebar (Hidden on mobile, persistent on md+) -->
	<aside class="hidden md:flex w-64 bg-surface-900 border-r border-white/10 flex-col justify-between shrink-0 z-20 sticky top-0 h-screen">
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
					class="flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all {active
						? 'bg-gradient-to-r from-orbit-cyan/15 to-transparent text-orbit-cyan border-l-2 border-orbit-cyan font-semibold shadow-glow-cyan/10'
						: 'text-slate-300 hover:text-white hover:bg-surface-800/80'}"
				>
					<div class="flex items-center gap-3">
						<item.icon size={16} class={active ? 'text-orbit-cyan' : 'text-slate-400 group-hover:text-slate-200'} />
						<span>{item.label}</span>
					</div>
					{#if active}
						<span class="w-1.5 h-1.5 rounded-full bg-orbit-cyan shadow-glow-cyan"></span>
					{/if}
				</a>
			{/each}
		</nav>

		<!-- Bottom Telemetry & Daemon Status -->
		<div class="p-4 border-t border-white/10 bg-surface-850 space-y-3">
			<div class="flex items-center justify-between">
				<span class="text-[11px] font-mono text-slate-400">Daemon</span>
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
		<!-- Top Bar (Desktop header with status) -->
		<header class="hidden md:flex h-14 bg-surface-900/80 backdrop-blur-md border-b border-white/10 px-6 items-center justify-between shrink-0 z-10">
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
			<div class="bg-rose-950/80 border-b border-rose-600/30 px-4 sm:px-6 py-2.5 text-xs text-rose-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
				<div class="flex items-center gap-2">
					<ShieldAlert size={15} class="text-rose-400 shrink-0" />
					<span>Orbit Daemon unreachable. Make sure the Orbit core service is running.</span>
				</div>
				<button
					onclick={() => orbitStore.checkHealth()}
					class="px-2.5 py-1 rounded bg-rose-900 hover:bg-rose-800 text-rose-100 font-mono text-[11px] self-start sm:self-auto shrink-0"
				>
					Retry Connection
				</button>
			</div>
		{/if}

		<!-- Page Viewport -->
		<main class="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-6 md:space-y-8">
			{@render children()}
		</main>
	</div>
</div>
