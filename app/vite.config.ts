import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '');
	const targetApi = env.PUBLIC_API_URL || 'http://localhost:8000/api/v1';

	return {
		plugins: [sveltekit()],
		server: {
			port: 5173,
			proxy: {
				'/api/v1': {
					target: targetApi.replace(/\/api\/v1\/?$/, ''),
					changeOrigin: true,
					secure: false
				}
			}
		}
	};
});
