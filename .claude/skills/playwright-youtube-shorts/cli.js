#!/usr/bin/env node

/**
 * Simple CLI for YouTube Shorts transcript extraction
 * Usage: node cli.js <youtube-shorts-url>
 */

const { extractYouTubeShortsTranscript } = require('./scripts/extract-transcript.js');

async function main() {
    const url = process.argv[2];

    if (!url) {
        console.error('Error: YouTube Shorts URL required');
        console.error('');
        console.error('Usage:');
        console.error('  node cli.js <youtube-shorts-url>');
        console.error('');
        console.error('Example:');
        console.error('  node cli.js "https://www.youtube.com/shorts/VIDEO_ID"');
        console.error('');
        process.exit(1);
    }

    if (!url.includes('youtube.com/shorts/')) {
        console.error('Error: URL must be a YouTube Shorts URL (format: https://www.youtube.com/shorts/VIDEO_ID)');
        process.exit(1);
    }

    console.error(`Extracting transcript from: ${url}`);
    console.error('This may take 20-30 seconds...');

    try {
        const result = await extractYouTubeShortsTranscript(url);

        if (result.success) {
            console.log('\n=== TRANSCRIPT EXTRACTED SUCCESSFULLY ===');
            console.log(`URL: ${result.url}`);
            console.log(`Segments found: ${result.segments.length}`);
            console.log(`Transcript length: ${result.transcript.length} characters`);
            console.log(`Has captions: ${result.metadata.hasCaptions}`);
            console.log('');

            if (result.transcript.trim()) {
                console.log('=== FULL TRANSCRIPT ===');
                console.log(result.transcript);
                console.log('');
            }

            if (result.segments.length > 0) {
                console.log('=== INDIVIDUAL SEGMENTS ===');
                result.segments.forEach((segment, index) => {
                    console.log(`${index + 1}. ${segment}`);
                });
            }

            // Also output JSON for programmatic use
            console.error('\n=== JSON OUTPUT (for programmatic use) ===');
            console.error('The full JSON result is available for parsing.');
        } else {
            console.error('\n=== EXTRACTION FAILED ===');
            console.error(`Error: ${result.error}`);
            console.error('');

            if (result.error.includes('Invalid URL')) {
                console.error('Please check the URL format. It should be:');
                console.error('  https://www.youtube.com/shorts/VIDEO_ID');
            } else {
                console.error('Possible reasons:');
                console.error('  1. Video has no captions/subtitles');
                console.error('  2. YouTube page structure changed');
                console.error('  3. Network or browser issues');
                console.error('');
                console.error('Try:');
                console.error('  1. Verify the video has captions (CC button)');
                console.error('  2. Check if video is available');
                console.error('  3. Run with DEBUG=true for more details');
            }

            process.exit(1);
        }
    } catch (error) {
        console.error(`\n=== UNEXPECTED ERROR ===`);
        console.error(error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error(`Fatal error: ${error.message}`);
        process.exit(1);
    });
}

module.exports = main;