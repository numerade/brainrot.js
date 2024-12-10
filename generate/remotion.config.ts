/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from '@remotion/cli/config';
import { enableTailwind } from '@remotion/tailwind';
import { getActualConcurrency } from '@remotion/renderer';

const concurrency = getActualConcurrency(); // Automatically resolves to 2

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setConcurrency(concurrency);
// Config.setChromiumMultiProcessOnLinux(true);

// This template processes the whole audio file on each thread which is heavy.
Config.overrideWebpackConfig((currentConfiguration) => {
	return enableTailwind(currentConfiguration);
});
