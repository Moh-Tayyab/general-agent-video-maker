// Simple test script
const { extractYouTubeShortsTranscript } = require('./scripts/extract-transcript.js');

async function test() {
    console.log('Testing YouTube Shorts transcript extractor...');

    // Test with a sample URL (this is a public Shorts URL that likely has captions)
    const testUrl = 'https://www.youtube.com/shorts/6G-tOjL5ug8';

    console.log(`Testing URL: ${testUrl}`);

    try {
        const result = await extractYouTubeShortsTranscript(testUrl);
        console.log('\nResult:');
        console.log(JSON.stringify(result, null, 2));

        if (result.success) {
            console.log('\n✅ SUCCESS!');
            console.log(`Transcript length: ${result.transcript.length} characters`);
            console.log(`Segments found: ${result.segments.length}`);

            if (result.segments.length > 0) {
                console.log('\nFirst few segments:');
                result.segments.slice(0, 3).forEach((seg, i) => {
                    console.log(`  ${i+1}. "${seg}"`);
                });
            }
        } else {
            console.log('\n❌ FAILED:');
            console.log(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('\n❌ UNEXPECTED ERROR:');
        console.error(error.message);
        console.error(error.stack);
    }
}

test();