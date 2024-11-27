<script>
	import Road from 'svelte-material-icons/Road.svelte';
	import Forest from 'svelte-material-icons/Forest.svelte';
	import SolarPanel from 'svelte-material-icons/SolarPanel.svelte';
	import PostLamp from 'svelte-material-icons/PostLamp.svelte';
	import Switch from 'svelte-material-icons/Switch.svelte';
	import Water from 'svelte-material-icons/Water.svelte';
	import ElevationRise from 'svelte-material-icons/ElevationRise.svelte';
	import GasBurner from 'svelte-material-icons/GasBurner.svelte';
	import Battery from 'svelte-material-icons/Battery.svelte';
	import LandFields from 'svelte-material-icons/LandFields.svelte';
	import ImageLayer from '$components/map/ImageLayer.svelte';
	import GeoJSONLayer from '$components/map/GeoJSONLayer.svelte';
	import { analyticsStore, currentAnalytic } from '$stores/analytics.js';

	export let api_url;
	export let currentPlot;

	const xyz_url = `${api_url}/images`;
	let selectedButtons = new Set();
	let title;

	$: title = $currentAnalytic;
	$: image = 'sites';
	$: bands = [1];
	$: stretch = [0, 1];
	$: palette = 'Reds';
	$: showRaster = false;
	$: geojsonLayers = new Map();

	const toggleLayer = async (layerId, fetchConfig) => {
		if (geojsonLayers.has(layerId)) {
			geojsonLayers.delete(layerId);
			selectedButtons.delete(layerId);
			if (geojsonLayers.size === 0) {
				currentAnalytic.set('');
			}
		} else {
			const response = await fetch(fetchConfig.url);
			const data = await response.json();
			if (!data || Object.keys(data).length === 0) {
				alert('No data found for this layer');
				return;
			}
			geojsonLayers.set(layerId, {
				data: data,
				options: fetchConfig.options
			});
			selectedButtons.add(layerId);
			currentAnalytic.set(fetchConfig.title);
		}
		selectedButtons = new Set(selectedButtons);
		geojsonLayers = new Map(geojsonLayers);
	};

	const fetchRoads = () =>
		toggleLayer('roads', {
			url: `${api_url}/analytics/roads`,
			title: 'Road Network',
			options: {
				style: {
					fillOpacity: 0,
					weight: 3,
					color: '#FF9800',
					dashArray: '10, 5',
					opacity: 0.8
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchPowerLines = () =>
		toggleLayer('power-lines', {
			url: `${api_url}/analytics/power_lines`,
			title: 'Power Lines',
			options: {
				style: {
					fillOpacity: 0,
					weight: 2.5,
					color: '#FFD700',
					dashArray: '15, 10, 5, 10',
					opacity: 0.9
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchPowerPlants = async () =>
		toggleLayer('power-plants', {
			url: `${api_url}/analytics/power_polygons`,
			title: 'Power Plants',
			options: {
				style: {
					fillOpacity: 0.6,
					weight: 2,
					color: '#FF5722',
					fillColor: '#FFAB91',
					dashArray: '5, 5'
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchPowerPoints = async () =>
		toggleLayer('power-points', {
			url: `${api_url}/analytics/power_points`,
			title: 'Power Points',
			options: {
				style: {
					fillOpacity: 0.6,
					weight: 2,
					color: '#3F51B5',
					fillColor: '#C5CAE9',
					dashArray: '5, 5'
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchPipelines = async () =>
		toggleLayer('gas-pipelines', {
			url: `${api_url}/analytics/pipelines`,
			title: 'Gas pipelines',
			options: {
				style: {
					fillOpacity: 0.6,
					weight: 2,
					color: '#4CAF50',
					fillColor: '#A5D6A7',
					dashArray: '5, 5'
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchWaterways = async () =>
		toggleLayer('water', {
			url: `${api_url}/analytics/waterways`,
			title: 'Hydrological Network',
			options: {
				style: {
					fillOpacity: 0.3,
					weight: 3,
					color: '#2196F3',
					opacity: 0.8
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchProtected = () =>
		toggleLayer('protected', {
			url: `${api_url}/analytics/protected_areas`,
			title: 'Protected Areas',
			options: {
				style: {
					fillOpacity: 0.4,
					weight: 2,
					color: '#4CAF50', // Verde más vibrante
					fillColor: '#81C784', // Verde más claro para el relleno
					dashArray: '5, 10'
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchSites = () =>
		toggleLayer('sites', {
			url: `${api_url}/analytics/suitable_areas`,
			title: 'Viable Sites',
			options: {
				style: {
					fillOpacity: 0.7,
					weight: 2,
					color: '#FF5722',
					fillColor: '#FFCCBC',
					dashArray: '3, 3'
				},
				pane: 'aoi',
				zIndex: 0
			}
		});

	const fetchElevation = async () => {
		const response = await fetch(`${api_url}/dem`);
		const data = await response.json();
		stretch = [data.min, data.max];
		toggleRaster({
			id: 'elevation',
			image: 'dem',
			title: 'Elevation',
			bands: [1],
			stretch: stretch,
			palette: 'terrain'
		});
	};

	const fetchLandcover = () =>
		toggleRaster({
			id: 'landuse',
			image: 'landcover',
			title: 'Land Cover',
			bands: [1],
			stretch: [10, 100],
			palette: 'Accent'
		});

	const toggleRaster = async (config) => {
		if (showRaster && image === config.image) {
			showRaster = false;
			selectedButtons.delete(config.id);
			currentAnalytic.set('');
		} else {
			showRaster = true;
			image = config.image;
			bands = config.bands;
			stretch = config.stretch;
			palette = config.palette;
			selectedButtons.add(config.id);
			currentAnalytic.set(config.title);
		}
		selectedButtons = new Set(selectedButtons);
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
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('water') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchWaterways}
>
	<Water size="100%" />
</button>

<button
	data-tip="Protected areas"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('protected') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchProtected}
>
	<Forest size="100%" />
</button>

<button
	data-tip="Elevation"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('elevation') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchElevation}
>
	<ElevationRise size="100%" />
</button>

<button
	data-tip="Land Cover"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('landuse') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchLandcover}
>
	<LandFields size="100%" />
</button>

<h1>Utilities layers</h1>
<button
	data-tip="Road Network"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('roads') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchRoads}
>
	<Road size="100%" />
</button>

<button
	data-tip="Power Lines"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('power-lines') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPowerLines}
>
	<PostLamp size="100%" />
</button>

<button
	data-tip="Power Plants"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('power-plants') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPowerPlants}
>
	<Switch size="100%" />
</button>

<button
	data-tip="Power Points"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('power-points') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPowerPoints}
>
	<Battery size="100%" />
</button>

<button
	data-tip="Gas pipelines"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('gas-pipelines') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchPipelines}
>
	<GasBurner size="100%" />
</button>

<h1>Viable sites</h1>

<button
	data-tip="Solar Sites"
	class={`w-10 h-10 p-1 hover:bg-gray-100 ${selectedButtons.has('sites') ? 'text-green-600' : 'text-gray-800'} tooltip tooltip-bottom`}
	on:click={fetchSites}
>
	<SolarPanel size="100%" />
</button>

{#if showRaster}
	<ImageLayer
		XYZ_URL={xyz_url}
		name="image"
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

{#if geojsonLayers.size > 0}
	{#each [...geojsonLayers.entries()] as [layerId, layer]}
		<GeoJSONLayer name={layerId} geojson={layer.data} options={layer.options} />
	{/each}
{/if}
