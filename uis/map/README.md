# SPAI template dashboard

## Dashboard logic

The server side is managed in the `+page.server.js`, which serves data and env variables to `+page.svelte`. Inside `+page.svelte` there is the `Analytics` component, which will have the desired subanalytic components, such as `ForestMonitoring` or `WaterQuality`.

## Analytics modules

The analytics modules, which contain the icons and the Footer, are located in the `analytics` directory and are called from `Analytics.svelte`. The data is also managed from there, and icons can be added or removed. To handle the `TimeLine` data, it is handled using `stores`, since it is `Svelte` 4.x.

To see material icons, go [here](https://github.com/ramiroaisen/svelte-material-icons/tree/master/svelte-material-icons).

## Env variables

Environment variables must be passed from the `+page.server.js` file to the `+page.svelte` file using `$props`.
