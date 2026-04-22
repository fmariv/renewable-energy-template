import { env } from '$env/dynamic/private';

export async function load({ fetch }) {
	const ENV = import.meta.env.VITE_ENV;
	const origin = ENV === 'PRO' ? 'https://' : 'http://';
	const api_url = env.API_URL ? `${origin}${env.API_URL}` : null;
	if (!api_url) {
		return { api_url: null, aoi: null };
	}

	let aoi = null;
	try {
		const aoiRes = await fetch(`${api_url}/aoi`);
		if (aoiRes.ok) {
			aoi = await aoiRes.json();
		}
	} catch (e) {
		console.error('Failed to fetch AOI', e);
	}

	return {
		api_url,
		aoi
	};
}