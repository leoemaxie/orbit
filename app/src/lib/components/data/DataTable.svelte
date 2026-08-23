<script lang="ts">
	import { Download, Filter, Search, ShieldCheck, ShieldAlert, FileText, CheckCircle2 } from '@lucide/svelte';
	import type { ResultOut } from '$lib/api/types';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		results: ResultOut[];
		title?: string;
	}

	let { results = [], title = 'Extracted Verified Telemetry Records' }: Props = $props();

	let searchQuery = $state('');
	let filterMode = $state<'all' | 'valid' | 'anomaly'>('all');

	// Extract unique dynamic columns across results
	const columns = $derived.by(() => {
		const cols = new Set<string>();
		for (const r of results) {
			if (r.data && typeof r.data === 'object') {
				Object.keys(r.data).forEach((k) => cols.add(k));
			}
		}
		return Array.from(cols);
	});

	// Filtered records
	const filteredResults = $derived.by(() => {
		return results.filter((r) => {
			// Validity filter
			if (filterMode === 'valid' && !r.valid) return false;
			if (filterMode === 'anomaly' && r.valid) return false;

			// Text search
			if (searchQuery.trim()) {
				const query = searchQuery.toLowerCase();
				const matchesUrl = r.url?.toLowerCase().includes(query);
				const matchesData = Object.values(r.data || {}).some((v) =>
					String(v).toLowerCase().includes(query)
				);
				return matchesUrl || matchesData;
			}
			return true;
		});
	});

	// CSV Export Handler
	function exportCSV() {
		if (results.length === 0) return;
		const headers = ['id', 'url', 'valid', ...columns];
		const rows = results.map((r) => {
			return [
				r.id,
				`"${r.url || ''}"`,
				r.valid ? 'true' : 'false',
				...columns.map((c) => {
					const val = r.data?.[c];
					return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val ?? '';
				})
			].join(',');
		});

		const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows].join('\n');
		const encodedUri = encodeURI(csvContent);
		const link = document.createElement('a');
		link.setAttribute('href', encodedUri);
		link.setAttribute('download', `orbit_data_${Date.now()}.csv`);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	// JSON Export Handler
	function exportJSON() {
		if (results.length === 0) return;
		const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(results, null, 2));
		const downloadAnchor = document.createElement('a');
		downloadAnchor.setAttribute('href', dataStr);
		downloadAnchor.setAttribute('download', `orbit_data_${Date.now()}.json`);
		document.body.appendChild(downloadAnchor);
		downloadAnchor.click();
		downloadAnchor.remove();
	}
</script>

<div class="space-y-4">
	<!-- Control Bar -->
	<div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3 bg-surface-900 border border-white/10 p-3 rounded-xl">
		<!-- Search & Filters -->
		<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 flex-1">
			<div class="relative flex-1 min-w-0">
				<Search size={14} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Filter records..."
					class="w-full pl-8 pr-3 py-1.5 bg-surface-800 border border-white/10 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-orbit-cyan/50 font-mono"
				/>
			</div>

			<!-- Filter Pills -->
			<div class="flex items-center gap-1 bg-surface-800 p-0.5 rounded-lg border border-white/5 font-mono text-xs overflow-x-auto">
				<button
					type="button"
					onclick={() => (filterMode = 'all')}
					class="px-2.5 py-1 rounded-md transition-colors whitespace-nowrap {filterMode === 'all' ? 'bg-surface-700 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}"
				>
					All ({results.length})
				</button>
				<button
					type="button"
					onclick={() => (filterMode = 'valid')}
					class="px-2.5 py-1 rounded-md transition-colors whitespace-nowrap {filterMode === 'valid' ? 'bg-emerald-950/80 text-emerald-400 font-medium' : 'text-slate-400 hover:text-slate-200'}"
				>
					Valid ({results.filter((r) => r.valid).length})
				</button>
				<button
					type="button"
					onclick={() => (filterMode = 'anomaly')}
					class="px-2.5 py-1 rounded-md transition-colors whitespace-nowrap {filterMode === 'anomaly' ? 'bg-rose-950/80 text-rose-400 font-medium' : 'text-slate-400 hover:text-slate-200'}"
				>
					Anomalies ({results.filter((r) => !r.valid).length})
				</button>
			</div>
		</div>

		<!-- Action Exports -->
		<div class="flex items-center gap-2 self-end lg:self-auto shrink-0">
			<Button variant="secondary" size="sm" onclick={exportCSV} disabled={results.length === 0}>
				<Download size={13} />
				<span>CSV</span>
			</Button>
			<Button variant="secondary" size="sm" onclick={exportJSON} disabled={results.length === 0}>
				<FileText size={13} />
				<span>JSON</span>
			</Button>
		</div>
	</div>

	<!-- High-Density Virtual Table -->
	<div class="border border-white/10 rounded-xl overflow-hidden bg-surface-900 shadow-2xl">
		<div class="overflow-x-auto max-h-[500px] overflow-y-auto">
			<table class="w-full text-left border-collapse font-sans text-xs">
				<thead class="sticky top-0 bg-surface-850 border-b border-white/10 text-[11px] font-mono uppercase text-slate-400 tracking-wider z-10">
					<tr>
						<th class="py-3 px-4 w-12 text-center">#</th>
						<th class="py-3 px-4 w-28">Status</th>
						{#each columns as col}
							<th class="py-3 px-4 text-slate-200 font-semibold">{col}</th>
						{/each}
						<th class="py-3 px-4">Source URL</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-white/5 font-mono">
					{#each filteredResults as row, idx}
						<tr class="hover:bg-surface-800/60 transition-colors {row.valid ? '' : 'bg-rose-950/10'}">
							<td class="py-2.5 px-4 text-center text-slate-500">{idx + 1}</td>
							<td class="py-2.5 px-4">
								{#if row.valid}
									<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-emerald-950/50 text-emerald-400 border border-emerald-500/30">
										<CheckCircle2 size={11} /> PASSED
									</span>
								{:else}
									<span
										class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-rose-950/60 text-rose-400 border border-rose-500/30"
										title={row.validation_errors?.join('; ')}
									>
										<ShieldAlert size={11} /> ANOMALY
									</span>
								{/if}
							</td>

							{#each columns as col}
								<td class="py-2.5 px-4 text-slate-200 truncate max-w-xs font-sans">
									{row.data?.[col] !== undefined ? String(row.data[col]) : '—'}
								</td>
							{/each}

							<td class="py-2.5 px-4 text-slate-400 truncate max-w-xs font-mono text-[11px]">
								{#if row.url}
									<a href={row.url} target="_blank" rel="noreferrer" class="hover:text-orbit-cyan hover:underline">
										{row.url}
									</a>
								{:else}
									<span class="text-slate-600">—</span>
								{/if}
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan={columns.length + 3} class="py-12 text-center text-slate-500 font-mono">
								No extracted data records found.
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
