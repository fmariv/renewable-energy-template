<script>
	/**
	 * Portable SPAI pipeline status banner.
	 *
	 * Copy to: uis/<ui-name>/src/components/PipelineStatusBanner.svelte
	 * Mount at page level above the map (relative parent), not in the sidebar.
	 *
	 * Props:
	 *   api_url — base URL of the API that exposes GET /pipeline/status
	 */
	import { onMount, onDestroy } from 'svelte';

	export let api_url;

	const POLL_MS = 5000;
	const READY_HIDE_MS = 3000;
	const EP_TURQUOISE = '#00C9B1';

	let status = 'Idle';
	let message = '';
	let visible = true;
	let pollId = null;
	let hideTimeout = null;

	const isProcessing = (s) => s === 'Idle' || s === 'Building';

	const titleFor = (s) => {
		if (s === 'Error') return 'Error downloading data';
		if (s === 'Warning') return 'Heads up';
		if (s === 'Ready') return 'Your data is ready';
		return 'Preparing your data';
	};

	const subtitleFor = (s, msg) => {
		if (s === 'Error') return 'Check the logs or contact support.';
		if (s === 'Warning') return msg || 'Processing continues with incomplete layers.';
		if (s === 'Ready') return msg || 'Layers are available on the map.';
		return 'Downloading and processing the required layers. Please wait a few minutes…';
	};

	const cardStyle = (s) => {
		if (s === 'Error') return 'border-color: #FECACA; background: #FFF7F7;';
		if (s === 'Warning') return 'border-color: #FDE68A; background: #FFFBEB;';
		if (s === 'Ready') return 'border-color: #BBF7D0; background: #F0FDF4;';
		return 'border-color: #E5E7EB; background: #FFFFFF;';
	};

	const accentFor = (s) => {
		if (s === 'Error') return '#E11D48';
		if (s === 'Warning') return '#D97706';
		if (s === 'Ready') return '#16A34A';
		return EP_TURQUOISE;
	};

	const stopPolling = () => {
		if (pollId != null) {
			clearInterval(pollId);
			pollId = null;
		}
	};

	const fetchStatus = async () => {
		try {
			const res = await fetch(`${api_url}/pipeline/status`);
			if (!res.ok) return;
			const data = await res.json();
			const next = data.status || 'Idle';
			status = next;
			message = data.message || '';

			if (next === 'Ready') {
				stopPolling();
				visible = true;
				if (hideTimeout != null) clearTimeout(hideTimeout);
				hideTimeout = setTimeout(() => {
					visible = false;
				}, READY_HIDE_MS);
			} else if (next === 'Error') {
				stopPolling();
				visible = true;
			} else {
				visible = true;
			}
		} catch {
			// Keep previous state on network errors
		}
	};

	onMount(() => {
		fetchStatus();
		pollId = setInterval(fetchStatus, POLL_MS);
	});

	onDestroy(() => {
		stopPolling();
		if (hideTimeout != null) clearTimeout(hideTimeout);
	});
</script>

{#if visible}
	<div class="pointer-events-none absolute inset-x-0 top-3 z-[5000] flex justify-center px-3">
		<div
			class="flex w-full max-w-[440px] items-start gap-3 border px-4 py-3 shadow-md"
			style={`border-radius: 12px; ${cardStyle(status)}`}
			role="status"
			aria-live="polite"
		>
			{#if isProcessing(status)}
				<span
					class="mt-0.5 inline-block h-4 w-4 flex-shrink-0 animate-spin rounded-full border-2 border-transparent"
					style={`border-top-color: ${EP_TURQUOISE}; border-right-color: ${EP_TURQUOISE};`}
					aria-hidden="true"
				/>
			{:else}
				<span
					class="mt-1.5 h-2.5 w-2.5 flex-shrink-0 rounded-full"
					style={`background-color: ${accentFor(status)};`}
					aria-hidden="true"
				/>
			{/if}
			<div class="min-w-0 flex-1">
				<p class="text-sm font-semibold leading-snug text-neutral-800">{titleFor(status)}</p>
				<p class="mt-0.5 text-xs leading-snug text-neutral-600">
					{subtitleFor(status, message)}
				</p>
			</div>
		</div>
	</div>
{/if}
