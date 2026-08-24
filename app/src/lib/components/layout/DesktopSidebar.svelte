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
		<div class="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
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
	<div class="p-3 border-t border-white/10">
		<div
			class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg border {orbitStore.daemonConnected
				? 'bg-emerald-950/30 border-emerald-500/20'
				: 'bg-rose-950/40 border-rose-500/25'}"
		>
			<span
				class="w-2 h-2 rounded-full shrink-0 {orbitStore.daemonConnected
					? 'bg-emerald-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.6)]'
					: 'bg-rose-500 shadow-[0_0_6px_rgba(239,68,68,0.5)]'}"
			></span>
			<div class="flex-1 min-w-0">
				<p class="text-xs font-medium {orbitStore.daemonConnected ? 'text-emerald-300' : 'text-rose-300'}">
					{orbitStore.daemonConnected ? 'Daemon online' : 'Daemon offline'}
				</p>
				{#if orbitStore.health}
					<p class="text-[10px] text-slate-500 font-mono mt-0.5">{orbitStore.health.environment} · scheduler {orbitStore.health.scheduler_enabled ? 'on' : 'off'}</p>
				{/if}
			</div>
		</div>
	</div>
</aside>
