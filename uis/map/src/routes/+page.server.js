import { env } from '$env/dynamic/private';

// Here is the code for the server-side route. The environment variables are imported from the private environment file. 
// The load function is an async function that fetches data from the backend services, so the default analytic
// must be changed here. The data is then returned as an object.

export async function load({fetch}) {
	const api_url = 'https://' + env.API_URL;
	let res = [
		await fetch(`${api_url}/`),
		await fetch(`${api_url}/aoi`)
	];
	const [images, aoi] = await Promise.all(res.map(r => r.json()));
	return {
		api_url,
		aoi
	};
}