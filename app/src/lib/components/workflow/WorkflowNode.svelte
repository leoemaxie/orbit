<script lang="ts">
	import { Play, Search, FileText, Database, ShieldCheck, Cloud, MessageSquare, CheckCircle2 } from '@lucide/svelte';
	import type { WorkflowNodeData } from './types';

	interface Props {
		node: WorkflowNodeData;
		selected?: boolean;
		onSelect: (node: WorkflowNodeData) => void;
	}

	let { node, selected = false, onSelect }: Props = $props();

	const iconMap: Record<string, any> = {
		trigger: Play,
		discovery: Search,
		parsing: FileText,
		extraction: Database,
		dossier: ShieldCheck,
		storage: Cloud,
		notify: MessageSquare
	};

	const Icon = $derived(iconMap[node.category] || Database);

	const categoryStyles: Record<string, string> = {
		trigger: 'border-orbit-cyan/60 shadow-glow-cyan/20 bg-surface-900',
		discovery: 'border-orbit-violet/50 shadow-glow-violet/20 bg-surface-900',
		parsing: 'border-emerald-500/50 shadow-glow-emerald/20 bg-surface-900',
		extraction: 'border-amber-500/50 shadow-glow-amber/20 bg-surface-900',
		dossier: 'border-cyan-400/50 shadow-glow-cyan/20 bg-surface-900',
		storage: 'border-blue-500/50 shadow-glow-cyan/20 bg-surface-900',
		notify: 'border-purple-500/50 shadow-glow-violet/20 bg-surface-900'
	};
</script>

<div
	role="button"
	tabindex="0"
	onclick={() => onSelect(node)}
	onkeydown={(e) => e.key === 'Enter' && onSelect(node)}
	class="w-56 p-3.5 rounded-xl border transition-all duration-200 cursor-pointer select-none text-left relative group hover:scale-[1.02] {categoryStyles[node.category]} {selected ? 'ring-2 ring-white ring-offset-2 ring-offset-void' : ''}"
>
	<!-- Input Connector Dot -->
	<div class="absolute -left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-surface-800 border-2 border-white/40 group-hover:border-orbit-cyan"></div>

	<!-- Node Header -->
	<div class="flex items-center justify-between gap-2 mb-2">
		<div class="p-1.5 rounded-lg bg-surface-800 border border-white/10 text-white">
			<Icon size={15} />
		</div>
		<span class="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-surface-800 text-slate-300 border border-white/5">
			{node.category}
		</span>
	</div>

	<!-- Node Content -->
	<div>
		<div class="text-xs font-semibold text-slate-100 group-hover:text-orbit-cyan transition-colors">{node.label}</div>
		<div class="text-[11px] font-mono text-slate-400 line-clamp-1 mt-0.5">{node.description}</div>
	</div>

	<!-- Output Connector Dot -->
	<div class="absolute -right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-surface-800 border-2 border-white/40 group-hover:border-orbit-cyan"></div>
</div>
