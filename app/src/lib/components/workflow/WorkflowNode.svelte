<script lang="ts">
	import { Play, Search, Globe, FileText, Database, ShieldCheck, Cloud, MessageSquare, Mail, Sparkles, Trash2, GripVertical } from '@lucide/svelte';
	import type { WorkflowNodeData } from './types';

	interface Props {
		node: WorkflowNodeData;
		selected?: boolean;
		onSelect: (node: WorkflowNodeData) => void;
		onDelete: (id: string) => void;
		onDragNodeStart: (e: MouseEvent, node: WorkflowNodeData) => void;
	}

	let { node, selected = false, onSelect, onDelete, onDragNodeStart }: Props = $props();

	const iconNameMap: Record<string, any> = {
		Play,
		Search,
		Globe,
		FileText,
		Database,
		ShieldCheck,
		Cloud,
		MessageSquare,
		Mail,
		Sparkles
	};

	const iconCategoryMap: Record<string, any> = {
		trigger: Play,
		discovery: Globe,
		parsing: FileText,
		extraction: Database,
		dossier: Sparkles,
		compliance: ShieldCheck,
		storage: Database,
		notify: MessageSquare
	};

	const Icon = $derived(iconNameMap[node.iconName] || iconCategoryMap[node.category] || Database);
</script>

<div
	role="button"
	tabindex="0"
	style="left: {node.x}px; top: {node.y}px; width: 220px;"
	onclick={() => onSelect(node)}
	onkeydown={(e) => e.key === 'Enter' && onSelect(node)}
	class="absolute z-10 p-3 rounded-xl border border-white/10 bg-surface-900/95 hover:border-orbit-cyan/60 transition-shadow select-none cursor-pointer group shadow-lg backdrop-blur-md {selected ? 'ring-2 ring-orbit-cyan ring-offset-2 ring-offset-void' : ''}"
>
	<!-- Input Port Dot -->
	<div class="absolute -left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-surface-800 border-2 border-white/40 group-hover:border-orbit-cyan"></div>

	<!-- Header & Drag Grip -->
	<div class="flex items-center justify-between gap-1 mb-1.5">
		<div
			class="flex items-center gap-1.5 cursor-grab active:cursor-grabbing text-slate-400 hover:text-white"
			onmousedown={(e) => onDragNodeStart(e, node)}
			role="button"
			tabindex="0"
		>
			<GripVertical size={13} />
			<div class="p-1 rounded bg-surface-800 text-orbit-cyan border border-white/5">
				<Icon size={13} />
			</div>
		</div>

		<div class="flex items-center gap-1">
			<span class="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-surface-800 text-slate-400 border border-white/5">
				{node.category}
			</span>
			<button
				type="button"
				onclick={(e) => { e.stopPropagation(); onDelete(node.id); }}
				class="p-0.5 rounded text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 opacity-0 group-hover:opacity-100 transition-opacity"
				title="Delete Node"
			>
				<Trash2 size={12} />
			</button>
		</div>
	</div>

	<!-- Content -->
	<div>
		<div class="text-xs font-semibold text-slate-100 group-hover:text-orbit-cyan transition-colors truncate">{node.label}</div>
		<div class="text-[11px] font-mono text-slate-400 line-clamp-1 mt-0.5">{node.description}</div>
	</div>

	<!-- Output Port Dot -->
	<div class="absolute -right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-surface-800 border-2 border-white/40 group-hover:border-orbit-cyan"></div>
</div>
