<script lang="ts">
	import { page } from '$app/state';
	import type { Component } from 'svelte';
	import { orbitStore } from '$lib/state/orbit.svelte';
	import OrbitLogo from '$lib/components/ui/OrbitLogo.svelte';

	interface NavItem {
		href: string;
		label: string;
		icon: Component<{ size?: number; class?: string }>;
	}

	interface Props {
		navItems: NavItem[];
	}

	let { navItems }: Props = $props();
</script>

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
