import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		allowedHosts: true,
	  },
	build: {
		rollupOptions: {
			output: {
				manualChunks(id) {
					if (id.includes('node_modules')) {
						return 'vendor';
					}
					if (id.includes('src/components')) {
						return 'components';
					}
					if (id.includes('src/routes')) {
						return 'routes';
					}
				}
			}
		}
	}
});


