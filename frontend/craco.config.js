const path = require('path');

module.exports = {
    webpack: {
        configure: (webpackConfig, { env, paths }) => {
            // Fix webpack-dev-server deprecation warnings by overriding devServer config
            if (env === 'development') {
                // Completely override the devServer configuration
                webpackConfig.devServer = {
                    ...webpackConfig.devServer,
                    // Remove deprecated options
                    onBeforeSetupMiddleware: undefined,
                    onAfterSetupMiddleware: undefined,
                    // Use the new setupMiddlewares option
                    setupMiddlewares: (middlewares, devServer) => {
                        if (!devServer) {
                            throw new Error('webpack-dev-server is not defined');
                        }

                        // Add any custom middleware here if needed
                        return middlewares;
                    },
                };
            }

            return webpackConfig;
        },
    },
    devServer: (devServerConfig, { env, paths, proxy, allowedHost }) => {
        // Override the entire devServer configuration
        return {
            ...devServerConfig,
            // Remove deprecated middleware options
            onBeforeSetupMiddleware: undefined,
            onAfterSetupMiddleware: undefined,
            // Use the new setupMiddlewares option
            setupMiddlewares: (middlewares, devServer) => {
                if (!devServer) {
                    throw new Error('webpack-dev-server is not defined');
                }

                // You can add custom middleware here
                // Example:
                // devServer.app.get('/api/health', (req, res) => {
                //   res.json({ status: 'ok' });
                // });

                return middlewares;
            },
            // Suppress other potential warnings
            client: {
                ...devServerConfig.client,
                logging: 'warn', // Reduce console output
                overlay: {
                    errors: true,
                    warnings: false, // Hide warnings in overlay
                },
            },
        };
    },
};
