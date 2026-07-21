<script>
	import { onMount, onDestroy } from 'svelte';

	export let api_url;

	const POLL_MS = 5000;
	const READY_HIDE_MS = 3000;

	let status = 'Idle';
	let message = '';
	let visible = true;
	let pollId = null;
	let hideTimeout = null;

	const headlineFor = (s) => {
		if (s === 'Error') return 'Pipeline failed';
		if (s === 'Warning') return 'Pipeline warning';
		if (s === 'Ready') return 'Pipeline completed';
		return 'Data is still being downloaded and processed, please wait';
	};

	const alertClass = (s) => {
		if (s === 'Error') return 'alert-error';
		if (s === 'Warning') return 'alert-warning';
		if (s === 'Ready') return 'alert-success';
		return 'alert-info';
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
			status = data.status || 'Idle';
			message = data.message || '';

			if (status === 'Ready') {
				stopPolling();
				visible = true;
				if (hideTimeout != null) clearTimeout(hideTimeout);
				hideTimeout = setTimeout(() => {
					visible = false;
				}, READY_HIDE_MS);
			} else if (status === 'Error') {
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
	<div class={`alert ${alertClass(status)} mb-3 text-sm shadow-sm`} role="status">
		<div>
			<p class="font-semibold leading-snug">{headlineFor(status)}</p>
			{#if message}
				<p class="mt-1 opacity-80 leading-snug">{message}</p>
			{/if}
		</div>
	</div>
{/if}
