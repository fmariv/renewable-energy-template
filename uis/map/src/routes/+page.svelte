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

<div class="box-border flex min-h-0 flex-1 flex-row gap-3 p-3">
	<div class="flex min-h-0 min-w-0 flex-1 flex-col gap-3">
		<div class="h-full min-h-0 min-w-0 flex-1">
		<Map
			zoom={6}
			panes={[
				{ name: 'aoi', zIndex: 9999 },
				{ name: 'left', zIndex: 999 }
			]}
			{aoi}
		>
			{#if layer == 'light'}
				<TileLayer
					url={'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png'}
					options={{ maxZoom: 20, zIndex: 1 }}
				/>
			{:else if layer == 'satellite'}
				<TileLayer
					url={'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'}
					options={{ maxZoom: 20, zIndex: 1 }}
				/>
			{:else if layer == 'streets'}
				<TileLayer
					url={'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'}
					options={{ maxZoom: 20, zIndex: 1 }}
				/>
			{:else if layer == 'dark'}
				<TileLayer
					url={'https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'}
					options={{ maxZoom: 20, zIndex: 1 }}
				/>
			{/if}
			<LayersControl layers={['satellite', 'light', 'dark', 'streets']} bind:layer />
		</Map>
		</div>
	</div>
	<div class="flex w-[200px] flex-shrink-0 flex-col overflow-y-auto">
		<Analytics {aoi} {api_url} />
	</div>
</div>
