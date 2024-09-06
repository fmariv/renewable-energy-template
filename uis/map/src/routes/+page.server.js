import { env } from '$env/dynamic/private';

// Here is the code for the server-side route. The environment variables are imported from the private environment file. 
// The load function is an async function that fetches data from the backend services, so the default analytic
// must be changed here. The data is then returned as an object.

export async function load({fetch}) {
	const xyz_url = 'http://' +  env.XYZ_URL;
	const analytics_url = 'http://' + env.ANALYTICS_URL;
	console.log(xyz_url, analytics_url)
	let res = [
		await fetch(`${xyz_url}/`),
		await fetch(`${analytics_url}/aoi`)
	];
	const [images, aoi] = await Promise.all(res.map(r => r.json()));
	return {
		xyz_url,
		analytics_url,
		aoi
	};
}