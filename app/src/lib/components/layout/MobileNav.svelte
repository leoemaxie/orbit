<script lang="ts">
	import { page } from '$app/state';
	import type { Component } from 'svelte';
	import { Menu, X } from '@lucide/svelte';
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
	let mobileMenuOpen = $state(false);

	function closeMenu() {
		mobileMenuOpen = false;
	}
</script>

<!-- Mobile Header Bar -->
<header class="md:hidden h-14 bg-surface-900 border-b border-white/10 px-4 flex items-center justify-between shrink-0 z-30 sticky top-0 backdrop-blur-md">
	<a href="/" onclick={closeMenu}>
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
		onclick={closeMenu}
	></div>

	<aside
		class="fixed top-0 left-0 bottom-0 w-72 bg-surface-900 border-r border-white/10 z-50 flex flex-col justify-between p-4 animate-in slide-in-from-left duration-200 md:hidden"
	>
		<div class="space-y-6">
			<!-- Brand Header in Mobile Drawer -->
			<div class="flex items-center justify-between pb-4 border-b border-white/10">
				<a href="/" onclick={closeMenu}>
					<OrbitLogo size="md" showWordmark={true} animated={true} />
				</a>
				<button
					type="button"
					onclick={closeMenu}
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
						onclick={closeMenu}
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
