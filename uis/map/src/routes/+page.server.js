import { env } from '$env/dynamic/private';

export async function load({ fetch }) {
	const ENV = import.meta.env.VITE_ENV;
	let origin = ENV === 'PRO' ? 'https://' : 'http://';
	const api_url = `${origin}${env.API_URL}`;

	const safeFetch = async (path) => {
		try {
			const res = await fetch(`${api_url}${path}`);
			if (res.ok) return await res.json();
		} catch {
			// API may be unavailable during bootstrap
		}
		return null;
	};

	const [root, aoi] = await Promise.all([safeFetch('/'), safeFetch('/aoi')]);

	return {
		api_url,
		aoi: aoi ?? null,
		images: root ?? null
	};
}
