---
name: playwright-youtube-shorts
description: Extract transcripts/captions from YouTube Shorts videos using Playwright automation. Use this skill whenever the user needs to get text content from YouTube Shorts URLs for AI script generation, content analysis, or automated content pipelines. This skill handles browser automation to fetch captions and returns clean transcript text.
---

# YouTube Shorts Transcript Extractor

This skill uses Playwright to automate browser interaction with YouTube Shorts, extract captions/transcripts, and return clean text for AI processing.

## When to Use This Skill

Use this skill when:
- You need to **experiment with YouTube Shorts automation**
- You want to **extract text content** from YouTube Shorts pages
- You're **prototyping AI content pipelines** for Shorts
- The user asks for **Playwright-based YouTube automation**
- You need a **starting point for more advanced extraction**

**Realistic expectations:**
- May extract UI text, navigation elements, or actual captions
- Success depends on video having detectable captions
- Use for prototyping, not production-critical extraction

Do NOT use this skill for:
- **Production caption extraction** (use YouTube API)
- **Guaranteed caption retrieval** (success not guaranteed)
- **Live streams or premium content**
- **Videos without enabled captions**

## Prerequisites

1. **Node.js v16+** installed
2. **Playwright** installed (the skill will install it if missing)
3. **Chromium browser** (Playwright will download it automatically)

## Quick Start

1. **Provide a YouTube Shorts URL** (e.g., `https://www.youtube.com/shorts/VIDEO_ID`)
2. **The skill will:**
   - Launch a headless browser
   - Navigate to the Shorts URL
   - Wait for captions to load
   - Extract all caption segments
   - Return cleaned transcript text

## Important Limitations

**This skill has known limitations due to YouTube's dynamic structure:**

1. **Captions may not be extracted** if:
   - The video doesn't have captions/subtitles enabled
   - YouTube has updated their page structure
   - Captions are embedded in the video (burned-in)

2. **The skill extracts text from the page**, which may include:
   - Actual video captions (if available and detectable)
   - UI elements (buttons, labels, navigation)
   - Page metadata and scripts

3. **Success rate varies** by video and region.

**For reliable caption extraction, consider:**
- Using YouTube's official API (requires authentication)
- Manual verification that the video has CC captions
- Alternative methods like speech-to-text services

## Best Use Cases

This skill works best for:
- Quick prototyping of YouTube Shorts automation
- Videos with clearly detectable captions
- Non-critical extraction tasks
- Learning Playwright automation with YouTube

## Claude Code Integration

When using this skill in Claude Code:

1. **Install the skill** (already done if skill is loaded)
2. **Provide a YouTube Shorts URL**
3. **Run the extraction script:**

```bash
cd /home/muhammad_tayyab/.claude/skills/playwright-youtube-shorts
node cli.js "https://www.youtube.com/shorts/VIDEO_ID"
```

4. **Parse the output** - the script prints both human-readable and JSON output

### Example Claude Code Workflow

```javascript
// In a Claude Code session:
const { execSync } = require('child_process');
const youtubeUrl = 'https://www.youtube.com/shorts/abc123';

try {
    const result = execSync(
        `node /home/muhammad_tayyab/.claude/skills/playwright-youtube-shorts/cli.js "${youtubeUrl}"`,
        { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }
    );
    console.log('Transcript extracted:', result);
} catch (error) {
    console.error('Extraction failed:', error.message);
}
```

### For AI Script Generation Pipeline

```
YouTube Shorts URL → Playwright Extraction → Transcript Text → 
Claude AI → 45-second Script + Timings → Voice-over → Final Video
```

## MCP Server Integration

This skill includes a Model Context Protocol (MCP) server that exposes the transcript extraction as a tool for Claude Code. The MCP server allows Claude Code to call the extraction function directly without needing to run external scripts.

### Configuration

Add the following to your Claude Code settings (`~/.claude/settings.json` or `.claude/settings.json`):

```json
{
  "mcpServers": {
    "youtube-shorts-transcript-extractor": {
      "command": "node",
      "args": ["/home/muhammad_tayyab/.claude/skills/playwright-youtube-shorts/mcp-server/server.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

Or create a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "youtube-shorts-transcript-extractor": {
      "command": "node",
      "args": ["/home/muhammad_tayyab/.claude/skills/playwright-youtube-shorts/mcp-server/server.js"]
    }
  }
}
```

### Available Tool

Once configured, Claude Code will have access to the `extract_youtube_shorts_transcript` tool:

- **Name**: `extract_youtube_shorts_transcript`
- **Description**: Extract transcript/captions from a YouTube Shorts video URL
- **Parameters**: `url` (YouTube Shorts URL in format: `https://www.youtube.com/shorts/VIDEO_ID`)

### Usage Example

When the MCP server is enabled, you can ask Claude Code to:
- "Extract transcript from this YouTube Shorts URL: https://www.youtube.com/shorts/abc123"
- "Get captions from this Shorts video"
- "Use the YouTube Shorts transcript tool on this URL"

The tool will return the same JSON format as the CLI.

## Output Format

The skill returns a JSON object with:
```json
{
  "success": true,
  "transcript": "Full transcript text...",
  "segments": ["Caption 1", "Caption 2", ...],
  "url": "Original YouTube Shorts URL",
  "error": null
}
```

If unsuccessful:
```json
{
  "success": false,
  "transcript": "",
  "segments": [],
  "url": "Original URL",
  "error": "Error description"
}
```

## Implementation Details

### Caption Extraction Strategy

YouTube Shorts display captions as overlayed text elements. The skill:
1. Waits for the video to load and captions to appear
2. Uses multiple selector strategies to find caption elements:
   - `yt-formatted-string.ytd-caption-segment-renderer`
   - `div.ytp-caption-segment`
   - CSS selectors for different caption formats
3. Aggregates captions across the video duration
4. Cleans and deduplicates text

### Installation Script

The skill includes an installation script that:
- Checks for Node.js
- Installs Playwright if missing
- Downloads browser binaries

## Step-by-Step Instructions

### 1. Check Dependencies

First, ensure Node.js is installed and install Playwright if needed:

```bash
node --version
npm install playwright
npx playwright install chromium
```

### 2. Create Extraction Script

Create a script `extract-transcript.js`:

```javascript
const { chromium } = require('playwright');

async function extractYouTubeShortsTranscript(url) {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    try {
        console.log(`Navigating to: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle' });
        
        // Wait for video and captions to load
        await page.waitForTimeout(5000);
        
        // Try multiple selector strategies for captions
        const selectors = [
            'yt-formatted-string.ytd-caption-segment-renderer',
            'div.ytp-caption-segment',
            '[class*="caption"][class*="segment"]',
            '.ytp-caption-segment'
        ];
        
        let allCaptions = [];
        for (const selector of selectors) {
            try {
                const captions = await page.$$eval(selector, elements => 
                    elements.map(el => el.textContent.trim()).filter(text => text.length > 0)
                );
                if (captions.length > 0) {
                    allCaptions = [...allCaptions, ...captions];
                }
            } catch (e) {
                // Selector not found, continue
            }
        }
        
        // Remove duplicates while preserving order
        const uniqueCaptions = [...new Set(allCaptions)];
        const transcript = uniqueCaptions.join(' ');
        
        await browser.close();
        
        return {
            success: true,
            transcript: transcript,
            segments: uniqueCaptions,
            url: url,
            error: null
        };
        
    } catch (error) {
        await browser.close();
        return {
            success: false,
            transcript: '',
            segments: [],
            url: url,
            error: error.message
        };
    }
}

// Command line execution
if (require.main === module) {
    const url = process.argv[2];
    if (!url) {
        console.error('Please provide a YouTube Shorts URL');
        console.error('Usage: node extract-transcript.js <youtube-shorts-url>');
        process.exit(1);
    }
    
    extractYouTubeShortsTranscript(url)
        .then(result => console.log(JSON.stringify(result, null, 2)))
        .catch(error => console.error(JSON.stringify({
            success: false,
            transcript: '',
            segments: [],
            url: url,
            error: error.message
        }, null, 2)));
}

module.exports = extractYouTubeShortsTranscript;
```

### 3. Run the Script

```bash
node extract-transcript.js "https://www.youtube.com/shorts/VIDEO_ID"
```

## Common Issues & Solutions

1. **No captions found**: Some Shorts don't have captions. Check if the video has CC option.
2. **Slow loading**: Increase wait time in script (line with `page.waitForTimeout(5000)`).
3. **Browser issues**: Ensure Playwright browsers are installed: `npx playwright install chromium`
4. **Selector changes**: YouTube may update CSS classes. Update selectors in the script.

## Integration with Claude Code

To use this skill in Claude Code workflows:

1. Save the extraction script
2. Call it from Node.js with the URL
3. Parse JSON output
4. Use transcript for AI script generation

## Example Workflow

```
YouTube Shorts URL → Playwright Script → Transcript → Claude AI → 45-sec Script + Timings
```

## Best Practices

1. **Rate limiting**: Add delays between requests to avoid YouTube restrictions
2. **Error handling**: Always implement try-catch for network issues
3. **Validation**: Check URL format before processing
4. **Caching**: Cache results for repeated requests to same URL

## Advanced: Caption Timing Extraction

For more advanced use cases (generating timed scripts), modify the script to capture timing information by monitoring caption changes over time.

## Troubleshooting

If the skill doesn't work:
1. Check browser installation: `npx playwright install --help`
2. Test with a known Shorts URL that has captions
3. Run in non-headless mode for debugging: `chromium.launch({ headless: false })`
4. Check network tab for any blocking resources

## Related Skills

- YouTube API skills for regular videos
- Video download and processing skills
- AI script generation skills
- Content pipeline automation skills