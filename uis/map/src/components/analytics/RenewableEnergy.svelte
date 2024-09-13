<script>
	import Road from 'svelte-material-icons/Road.svelte';
	import Forest from 'svelte-material-icons/Forest.svelte';
	import PostLamp from 'svelte-material-icons/PostLamp.svelte';
	import Switch from 'svelte-material-icons/Switch.svelte';
	import Water from 'svelte-material-icons/Water.svelte';
	import ElevationRise from 'svelte-material-icons/ElevationRise.svelte';
	import SlopeDownhill from 'svelte-material-icons/SlopeDownhill.svelte';
	import Castle from 'svelte-material-icons/Castle.svelte';
	import SunAngle from 'svelte-material-icons/SunAngle.svelte';
	import GasBurner from 'svelte-material-icons/GasBurner.svelte';
	import Battery from 'svelte-material-icons/Battery.svelte';
	import LandFields from 'svelte-material-icons/LandFields.svelte';
	import ImageLayer from '$components/map/ImageLayer.svelte';
	import GeoJSONLayer from '$components/map/GeoJSONLayer.svelte';
	import { analyticsStore, currentAnalytic } from '$stores/analytics.js';

	export let api_url;
	export let currentPlot;

	let title;

	$: title = $currentAnalytic;
	$: image = 'sites';
	$: bands = [1];
	$: stretch = [0, 1];
	$: palette = 'Reds';
	$: geojson = null;
	$: geojsonOptions = {};
	$: showRaster = false;

	let selectedButton = '';
	let selected = false;
	let xyz_url = `${api_url}/images`;

	const fetchRoads = async () => {
		if (selected && $currentAnalytic === 'Road Network') {
			selected = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		geojson = null;
		const response = await fetch(`${api_url}/analytics/roads`);
		const data = await response.json();
		if (Object.keys(data).length === 0) {
			alert('No roads found in the selected area.');
			return;
		}
		geojson = data;
		currentAnalytic.set('Road Network');
		geojsonOptions = {
			style: { fillOpacity: 0, weight: 2, color: 'black', dashArray: '5, 5' },
			pane: 'aoi',
			zIndex: 0
		};
		selectedButton = 'roads';
	};

	const fetchPowerLines = async () => {
		if (selected && $currentAnalytic === 'Power Lines') {
			selected = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		geojson = null;
		const response = await fetch(`${api_url}/analytics/power_lines`);
		const data = await response.json();
		if (Object.keys(data).length === 0) {
			alert('No power lines found in the selected area.');
			return;
		}
		geojson = data;
		currentAnalytic.set('Power Lines');
		geojsonOptions = {
			style: { fillOpacity: 0, weight: 2, color: 'black', dashArray: '5, 5' },
			pane: 'aoi',
			zIndex: 0
		};
		selectedButton = 'power-lines';
	};

	const fetchPowerPlants = async () => {
		if (selected && $currentAnalytic === 'Power Plants') {
			selected = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		geojson = null;
		const response = await fetch(`${api_url}/analytics/power_polygons`);
		const data = await response.json();
		if (Object.keys(data).length === 0) {
			alert('No power plants found in the selected area.');
			return;
		}
		geojson = data;
		currentAnalytic.set('Power Plants');
		geojsonOptions = {
			pointToLayer: function (feature, latlng) {
				return L.circleMarker(latlng, {
					radius: 8,
					fillColor: '#ff7800',
					color: '#000',
					weight: 1,
					opacity: 1,
					fillOpacity: 0.8
				});
			},
			pane: 'aoi',
			zIndex: 0
		};
		selectedButton = 'power-plants';
	};

	const fetchPowerPoints = async () => {
		if (selected && $currentAnalytic === 'Power Points') {
			selected = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		geojson = null;
		const response = await fetch(`${api_url}/analytics/power_points`);
		const data = await response.json();
		if (Object.keys(data).length === 0) {
			alert('No roads transformers in the selected area.');
			return;
		}
		geojson = data;
		currentAnalytic.set('Power Points');
		geojsonOptions = {
			pointToLayer: function (feature, latlng) {
				return L.circleMarker(latlng, {
					radius: 8,
					fillColor: '#ff7800',
					color: '#000',
					weight: 1,
					opacity: 1,
					fillOpacity: 0.8
				});
			},
			pane: 'aoi',
			zIndex: 0
		};
		selectedButton = 'power-points';
	};

	const fetchPipelines = async () => {
		if (selected && $currentAnalytic === 'Gas pipelines') {
			selected = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		geojson = null;
		const response = await fetch(`${api_url}/analytics/pipelines`);
		const data = await response.json();
		if (Object.keys(data).length === 0) {
			alert('No pipelines found in the selected area.');
			return;
		}
		geojson = data;
		currentAnalytic.set('Gas pipelines');
		geojsonOptions = {
			pointToLayer: function (feature, latlng) {
				return L.circleMarker(latlng, {
					radius: 8,
					fillColor: '#ff7800',
					color: '#000',
					weight: 1,
					opacity: 1,
					fillOpacity: 0.8
				});
			},
			pane: 'aoi',
			zIndex: 0
		};
		selectedButton = 'gas-pipelines';
	};

	const fetchWaterways = async () => {
		if (selected && $currentAnalytic === 'Hydrological Network') {
			selected = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		geojson = null;
		const response = await fetch(`${api_url}/analytics/waterways`);
		const data = await response.json();
		if (Object.keys(data).length === 0) {
			alert('No waterways found in the selected area.');
			return;
		}
		geojson = data;
		currentAnalytic.set('Hydrological Network');
		geojsonOptions = {
			style: { fillOpacity: 0, weight: 2, color: 'blue', dashArray: '' },
			pane: 'aoi',
			zIndex: 0
		};
		selectedButton = 'water';
	};

	const fetchElevation = async () => {
		if (selected && $currentAnalytic === 'Elevation') {
			selected = false;
			showRaster = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		if (!showRaster) {
			showRaster = true;
		}
		geojson = null;
		geojsonOptions = {};
		currentAnalytic.set('Elevation');
		image = `dem`;
		bands = [1];
		stretch = [293, 1117];
		palette = 'terrain';
		selectedButton = 'elevation';
	};

	const fetchLandcover = async () => {
		if (selected && $currentAnalytic === 'Land Cover') {
			selected = false;
			showRaster = false;
			selectedButton = '';
			currentAnalytic.set('');
			return;
		}
		if (!selected) {
			selected = true;
		}
		if (!showRaster) {
			showRaster = true;
		}
		geojson = null;
		geojsonOptions = {};
		currentAnalytic.set('Land Cover');
		image = `land_cover`;
		bands = [1];
		stretch = [10, 100];
		palette = 'Accent';
		selectedButton = 'landuse';
	};
</script>

<!-- Here is where the buttons are added to the component. If you want to add new analytics, you should
also add a fetch function and a new button. The fetch function should fetch the data from the server
and update the analytics store. The button should call the fetch function when clicked. 

To see Material icons, go here: https://github.com/ramiroaisen/svelte-material-icons/tree/master/svelte-material-icons
-->
<h1>Geophisical layers</h1>

<button
	data-tip="Hydrological Network"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'water' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchWaterways}
>
	<Water size="100%" />
</button>

<button
	data-tip="Elevation"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'elevation' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchElevation}
>
	<ElevationRise size="100%" />
</button>

<button
	data-tip="Land Cover"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'land-cover' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchLandcover}
>
	<LandFields size="100%" />
</button>

<h1>Utilities layers</h1>
<button
	data-tip="Road Network"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'roads' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchRoads}
>
	<Road size="100%" />
</button>

<button
	data-tip="Power Lines"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'power-lines' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPowerLines}
>
	<PostLamp size="100%" />
</button>

<button
	data-tip="Power Plants"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'power-plants' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPowerPlants}
>
	<Switch size="100%" />
</button>

<button
	data-tip="Power Points"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'power-points' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPowerPoints}
>
	<Battery size="100%" />
</button>

<button
	data-tip="Gas pipelines"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButton === 'gas-pipelines' ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPipelines}
>
	<GasBurner size="100%" />
</button>

{#if showRaster}
	<ImageLayer
		XYZ_URL={xyz_url}
		name="sites"
		image={image + '.tif'}
		options={{
			maxZoom: 20,
			pane: 'left'
		}}
		{bands}
		{stretch}
		{palette}
	/>
{/if}

{#if selected && geojson}
	<GeoJSONLayer name={'roads'} {geojson} options={geojsonOptions} fit={true} />
{/if}
