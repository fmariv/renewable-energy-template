<script>
	import Map from '$components/map/Map.svelte';
	import TileLayer from '$components/map/TileLayer.svelte';
	import LayersControl from '$components/map/LayersControl.svelte';
	import ImageLayer from '$components/map/ImageLayer.svelte';
	import GeoJSONLayer from '$components/map/GeoJSONLayer.svelte';
	import Analytics from '$components/Analytics.svelte';

	export let data;

	// Here we destructure the data object, which comes from the server
	// Environment variables are used to determine the value of the data object
	// The data object comes from +page.server.js
	$: ({ api_url, aoi } = data);

	let layer;
</script>

<div class="w-screen h-screen flex flex-row gap-3 p-3">
	<div class="flex flex-col flex-1 gap-3">
		<Map
			zoom={6}
			panes={[
				{ name: 'aoi', zIndex: 9999 },
				{ name: 'left', zIndex: 999 }
			]}
			{aoi}
		>
			{#if layer == 'streets'}
				<TileLayer
					url={`https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png`}
					options={{ maxZoom: 20, zIndex: 1 }}
				/>
			{:else if layer == 'satellite'}
				<TileLayer
					url={`https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`}
					options={{ maxZoom: 20, zIndex: 1 }}
				/>
			{/if}
			<LayersControl layers={['streets', 'satellite']} bind:layer />
		</Map>
	</div>
	<div class="w-[200px]">
		<Analytics {aoi} {api_url} />
	</div>
</div>
