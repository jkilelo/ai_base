// AI Base Project - Shared CRACO Configuration
// Webpack customization for React apps across all versions

const path = require('path');

module.exports = {
    webpack: {
        configure: (webpackConfig, { env, paths }) => {
            // Fix webpack-dev-server deprecation warnings
            if (env === 'development') {
                webpackConfig.devServer = {
                    ...webpackConfig.devServer,
                    onBeforeSetupMiddleware: undefined,
                    onAfterSetupMiddleware: undefined,
                    setupMiddlewares: (middlewares, devServer) => {
                        if (!devServer) {
                            throw new Error('webpack-dev-server is not defined');
                        }
                        return middlewares;
                    },
                };
            }

            // Add path aliases
            webpackConfig.resolve.alias = {
                ...webpackConfig.resolve.alias,
                '@': path.resolve(__dirname, 'src'),
                '@components': path.resolve(__dirname, 'src/components'),
                '@pages': path.resolve(__dirname, 'src/pages'),
                '@utils': path.resolve(__dirname, 'src/utils'),
                '@api': path.resolve(__dirname, 'src/api'),
                '@types': path.resolve(__dirname, 'src/types'),
                '@hooks': path.resolve(__dirname, 'src/hooks'),
                '@styles': path.resolve(__dirname, 'src/styles'),
            };

            return webpackConfig;
        },
    },
    devServer: (devServerConfig, { env, paths, proxy, allowedHost }) => {
        return {
            ...devServerConfig,
            onBeforeSetupMiddleware: undefined,
            onAfterSetupMiddleware: undefined,
            setupMiddlewares: (middlewares, devServer) => {
                if (!devServer) {
                    throw new Error('webpack-dev-server is not defined');
                }

                // Add custom API proxy if needed
                devServer.app.get('/api/health', (req, res) => {
                    res.json({
                        status: 'ok',
                        timestamp: new Date().toISOString(),
                        environment: process.env.REACT_APP_ENVIRONMENT || 'development'
                    });
                });

                return middlewares;
            },
            client: {
                ...devServerConfig.client,
                logging: 'warn',
                overlay: {
                    errors: true,
                    warnings: false,
                },
            },
            // Proxy API requests to FastAPI backend
            proxy: {
                '/api': {
                    target: process.env.REACT_APP_API_URL || 'http://localhost:8000',
                    changeOrigin: true,
                    secure: false,
                },
            },
        };
    },
    eslint: {
        enable: true,
        mode: 'extends',
    },
    babel: {
        plugins: [
            // Add any custom babel plugins here
        ],
    },
};
