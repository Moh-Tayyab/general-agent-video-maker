#!/usr/bin/env node

const { chromium } = require('playwright');

/**
 * Extract transcript/captions from YouTube Shorts
 * @param {string} url - YouTube Shorts URL
 * @returns {Promise<object>} Result object with transcript, segments, and status
 */
async function extractYouTubeShortsTranscript(url) {
    console.error(`Starting transcript extraction for: ${url}`);

    // Validate URL
    if (!url || !url.includes('youtube.com/shorts/')) {
        return {
            success: false,
            transcript: '',
            segments: [],
            url: url,
            error: 'Invalid YouTube Shorts URL. Must be in format: https://www.youtube.com/shorts/VIDEO_ID'
        };
    }

    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] // For Linux environments
    });
    const page = await browser.newPage();

    try {
        console.error('Launching browser...');

        // Navigate to URL with extended timeout
        console.error(`Navigating to URL...`);
        await page.goto(url, {
            waitUntil: 'domcontentloaded',
            timeout: 30000
        });

        // Wait for page to fully load
        console.error('Waiting for page load...');
        await page.waitForTimeout(10000); // Increased wait for Shorts

        // Try to play the video if it's not auto-playing
        console.error('Checking if video needs interaction...');
        try {
            const playButton = await page.$('button[aria-label="Play"], .ytp-play-button, .ytp-large-play-button, [class*="play-button"]');
            if (playButton) {
                console.error('Clicking play button...');
                await playButton.click();
                await page.waitForTimeout(3000);
            }
        } catch (playError) {
            console.error(`Could not click play button: ${playError.message}`);
        }

        // Scroll to trigger lazy loading if needed
        await page.evaluate(() => {
            window.scrollBy(0, 100);
        });
        await page.waitForTimeout(3000);

        // Wait a bit for captions to potentially appear
        console.error('Waiting for captions to load...');
        await page.waitForTimeout(5000);

        // Try to enable captions if CC button exists
        console.error('Looking for CC button...');
        try {
            const ccButton = await page.$('button.ytp-button[data-title-no-tooltip="Subtitles/closed captions"], button[aria-label*="captions"], button[aria-label*="CC"], .ytp-subtitles-button');
            if (ccButton) {
                console.error('Found CC button, clicking to enable captions...');
                await ccButton.click();
                await page.waitForTimeout(3000); // Wait for captions to appear
            }
        } catch (ccError) {
            console.error(`Could not click CC button: ${ccError.message}`);
        }

        // Multiple selector strategies for captions - YouTube Shorts specific
        const selectorStrategies = [
            // YouTube Shorts specific captions
            'ytd-shorts-player-controls .caption-container',
            '#caption-window .caption-visual-line',
            '.shorts-caption-container',
            'div[class*="shorts"][class*="caption"]',
            'ytd-shorts #caption-window',

            // YouTube player captions (might work for Shorts too)
            'div.ytp-caption-segment',
            'span.ytp-caption-segment',
            '.caption-window .caption-text',
            '#caption-window span',

            // Generic caption elements
            'yt-formatted-string.ytd-caption-segment-renderer',
            '[class*="caption"][class*="segment"]',
            '[class*="caption"][class*="text"]',
            '[class*="subtitle"]',
            '[class*="transcript"]',

            // Fallback: any visible text that might be captions
            'div[role="caption"]',
            '[aria-label*="caption"]',
            '[data-purpose="caption"]',
        ];

        console.error('Searching for captions with multiple selectors...');
        let allCaptions = [];

        for (const selector of selectorStrategies) {
            try {
                const captions = await page.$$eval(selector, elements =>
                    elements.map(el => {
                        const text = el.textContent || el.innerText || '';
                        return text.trim();
                    }).filter(text => text.length > 0)
                );

                if (captions.length > 0) {
                    console.error(`Found ${captions.length} captions with selector: ${selector}`);
                    allCaptions = [...allCaptions, ...captions];
                }
            } catch (error) {
                // Selector not found or error - continue to next strategy
                console.error(`Selector ${selector} failed: ${error.message}`);
            }
        }

        // Fallback: Try to get any text that looks like captions (not JS/CSS)
        if (allCaptions.length === 0) {
            console.error('Trying fallback text extraction...');
            try {
                const allText = await page.$$eval('*', elements =>
                    elements.map(el => {
                        const text = el.textContent || el.innerText || '';
                        return text.trim();
                    }).filter(text => {
                        // Filter out JavaScript, CSS, and UI elements
                        const lowerText = text.toLowerCase();
                        const isCode = text.includes('{') && text.includes('}') ||
                                       text.includes('function') ||
                                       text.includes('var ') ||
                                       text.includes('const ') ||
                                       text.includes('let ') ||
                                       text.includes('window.') ||
                                       text.includes('document.') ||
                                       text.includes('.style') ||
                                       text.includes('://');

                        const isUIElement = lowerText.includes('subscribe') ||
                                           lowerText.includes('like') ||
                                           lowerText.includes('share') ||
                                           lowerText.includes('comment') ||
                                           lowerText.includes('©') ||
                                           lowerText.includes('youtube') ||
                                           lowerText.includes('shorts');

                        const isReasonableLength = text.length > 5 && text.length < 200;
                        const isNotTimestamp = !text.match(/^\d+:\d+$/);

                        return isReasonableLength && isNotTimestamp && !isCode && !isUIElement;
                    })
                );

                // Deduplicate and take top candidates
                const uniqueText = [...new Set(allText)];
                allCaptions = uniqueText.slice(0, 30); // Limit to 30 potential captions

                console.error(`Fallback found ${allCaptions.length} potential caption segments`);
            } catch (error) {
                console.error(`Fallback extraction failed: ${error.message}`);
            }
        }

        // Remove duplicates while preserving order
        const uniqueCaptions = [];
        const seen = new Set();
        for (const caption of allCaptions) {
            const normalized = caption.toLowerCase().replace(/\s+/g, ' ');
            if (!seen.has(normalized) && caption.length > 0) {
                seen.add(normalized);
                uniqueCaptions.push(caption);
            }
        }

        const transcript = uniqueCaptions.join(' ');

        console.error(`Extraction complete. Found ${uniqueCaptions.length} unique caption segments.`);

        await browser.close();

        return {
            success: true,
            transcript: transcript,
            segments: uniqueCaptions,
            url: url,
            error: null,
            metadata: {
                segmentsCount: uniqueCaptions.length,
                transcriptLength: transcript.length,
                hasCaptions: uniqueCaptions.length > 0
            }
        };

    } catch (error) {
        console.error(`Error during extraction: ${error.message}`);

        try {
            await browser.close();
        } catch (closeError) {
            console.error(`Error closing browser: ${closeError.message}`);
        }

        return {
            success: false,
            transcript: '',
            segments: [],
            url: url,
            error: `Extraction failed: ${error.message}`,
            metadata: {
                segmentsCount: 0,
                transcriptLength: 0,
                hasCaptions: false
            }
        };
    }
}

/**
 * Install required dependencies
 */
async function installDependencies() {
    console.error('Checking dependencies...');

    try {
        // Check if Playwright is available
        require.resolve('playwright');
        console.error('Playwright is already installed.');
    } catch (error) {
        console.error('Playwright not found. Installing...');
        const { execSync } = require('child_process');

        try {
            execSync('npm install playwright', { stdio: 'inherit' });
            console.error('Playwright installed successfully.');

            console.error('Installing browser binaries...');
            execSync('npx playwright install chromium', { stdio: 'inherit' });
            console.error('Browser binaries installed.');
        } catch (installError) {
            console.error(`Installation failed: ${installError.message}`);
            return false;
        }
    }

    return true;
}

// Command line execution
async function main() {
    const url = process.argv[2];

    if (!url) {
        console.error('ERROR: Please provide a YouTube Shorts URL');
        console.error('Usage: node extract-transcript.js <youtube-shorts-url>');
        console.error('Example: node extract-transcript.js "https://www.youtube.com/shorts/abc123"');
        process.exit(1);
    }

    console.error(`YouTube Shorts Transcript Extractor`);
    console.error(`====================================`);

    // Check dependencies
    const depsInstalled = await installDependencies();
    if (!depsInstalled) {
        console.error(JSON.stringify({
            success: false,
            transcript: '',
            segments: [],
            url: url,
            error: 'Failed to install required dependencies'
        }, null, 2));
        process.exit(1);
    }

    // Extract transcript
    const result = await extractYouTubeShortsTranscript(url);

    // Output JSON result
    console.log(JSON.stringify(result, null, 2));

    // Exit with appropriate code
    process.exit(result.success ? 0 : 1);
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error(`Unhandled error: ${error.message}`);
        console.error(error.stack);
        console.log(JSON.stringify({
            success: false,
            transcript: '',
            segments: [],
            url: process.argv[2] || '',
            error: `Script error: ${error.message}`
        }, null, 2));
        process.exit(1);
    });
}

module.exports = {
    extractYouTubeShortsTranscript,
    installDependencies
};