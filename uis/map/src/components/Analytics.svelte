<script>
	import Map from 'svelte-material-icons/Map.svelte';
	import GeoJSONLayer from '$components/map/GeoJSONLayer.svelte';
	import RenewableEnergy from '$components/analytics/RenewableEnergy.svelte';

	export let aoi;
	export let api_url;

	let selected = true;
	const toggleAOI = () => {
		selected = !selected;
	};
</script>

<div>
	<!-- There are some components that already have the h1 title, i.e. Water Quality, so this code block can be omitted. -->
	<h1>Area of Interest</h1>
	<button
		class={`w-10 h-10 p-1 hover:bg-gray-100 'text-gray-800'} tooltip tooltip-bottom ${
			selected ? 'text-green-600' : 'text-gray-800'
		}`}
		on:click={toggleAOI}
		data-tip="Area of Interest"
	>
		<Map size="100%" />
	</button>
	<!-- Here is where the analytics will be displayed -->
	<!-- This is an example of how to import an analytics component -->
	<!-- <ForestMonitoring {analytics} {date} {xyz_url} {analytics_url} {left} /> -->
	<RenewableEnergy {api_url} />
</div>

{#if selected}
	<GeoJSONLayer
		name={'aoi'}
		options={{
			style: { fillOpacity: 0, weight: 4, color: 'red', dashArray: '' },
			pane: 'aoi',
			zIndex: 0
		}}
		geojson={aoi}
	/>
{/if}
