<script lang="ts">
	import WorkflowHeader from '$lib/components/workflow/WorkflowHeader.svelte';
	import WorkflowCanvas from '$lib/components/workflow/WorkflowCanvas.svelte';
	import WorkflowConfigPanel from '$lib/components/workflow/WorkflowConfigPanel.svelte';
	import type { WorkflowNodeData } from '$lib/components/workflow/types';

	const initialNodes: WorkflowNodeData[] = [
		{ id: '1', label: 'Mission Trigger', category: 'trigger', iconName: 'Play', description: 'Cron schedule / on-demand webhook', status: 'active', x: 0, y: 0, config: { frequency: 'daily', schedule_time: '08:00', timezone: 'UTC' } },
		{ id: '2', label: 'Proxy Discovery', category: 'discovery', iconName: 'Search', description: 'Multi-engine search & proxy retrieval', status: 'active', x: 1, y: 0, config: { search_depth: 2, max_sources: 8, proxy_zone: 'datacenter' } },
		{ id: '3', label: 'Document Parser', category: 'parsing', iconName: 'FileText', description: 'Layout & table deconstruction', status: 'active', x: 2, y: 0, config: { layout_analysis: true, ocr_enabled: true, table_format: 'markdown' } },
		{ id: '4', label: 'Schema Extractor', category: 'extraction', iconName: 'Database', description: 'LLM structured record parsing & anomaly check', status: 'active', x: 3, y: 0, config: { temperature: 0.1, anomaly_detection: true } },
		{ id: '5', label: 'Dossier & Redaction', category: 'dossier', iconName: 'ShieldCheck', description: 'Executive HTML brief & PII masking', status: 'active', x: 4, y: 0, config: { format: 'pdf', pii_redaction: true, entity_types: 'EMAIL,SSN,CREDIT_CARD' } },
		{ id: '6', label: 'S3 Cloud Storage', category: 'storage', iconName: 'Cloud', description: 'Presigned URL & bucket archival', status: 'active', x: 5, y: 0, config: { bucket_name: 'orbit-exports', region: 'us-east-1', prefix: 'dossiers' } },
		{ id: '7', label: 'Slack Alert Sink', category: 'notify', iconName: 'MessageSquare', description: 'Notification blocks with dossier link', status: 'active', x: 6, y: 0, config: { webhook_enabled: true, channel: '#orbit-alerts', include_dossier_button: true } }
	];

	let nodes = $state<WorkflowNodeData[]>(JSON.parse(JSON.stringify(initialNodes)));
	let selectedNode = $state<WorkflowNodeData | null>(null);
	let deploying = $state(false);

	function handleSelectNode(node: WorkflowNodeData) {
		selectedNode = node;
	}

	function handleSaveConfig(updatedConfig: Record<string, any>) {
		if (!selectedNode) return;
		const idx = nodes.findIndex((n) => n.id === selectedNode?.id);
		if (idx !== -1) {
			nodes[idx].config = updatedConfig;
			selectedNode = { ...nodes[idx] };
		}
	}

	async function handleDeploy() {
		deploying = true;
		setTimeout(() => (deploying = false), 1200);
	}

	function handleReset() {
		nodes = JSON.parse(JSON.stringify(initialNodes));
		selectedNode = null;
	}
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<WorkflowHeader onDeploy={handleDeploy} onReset={handleReset} {deploying} />

	<div class="space-y-6">
		<WorkflowCanvas
			{nodes}
			edges={[]}
			{selectedNode}
			onSelectNode={handleSelectNode}
		/>

		{#if selectedNode}
			<WorkflowConfigPanel
				node={selectedNode}
				onClose={() => (selectedNode = null)}
				onSave={handleSaveConfig}
			/>
		{/if}
	</div>
</div>
