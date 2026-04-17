#!/usr/bin/env node

/**
 * MCP Server for YouTube Shorts Transcript Extraction
 *
 * This server exposes a tool for extracting transcripts/captions from YouTube Shorts videos
 * using Playwright automation.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { ListToolsRequestSchema, CallToolRequestSchema } = require('@modelcontextprotocol/sdk/types.js');

// Import our extraction function
const { extractYouTubeShortsTranscript } = require('../scripts/extract-transcript.js');

// Create MCP server
const server = new Server(
  {
    name: 'youtube-shorts-transcript-extractor',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {}, // We'll add tools dynamically
    },
  }
);

// Define the transcript extraction tool
const extractTranscriptTool = {
  name: 'extract_youtube_shorts_transcript',
  description: 'Extract transcript/captions from a YouTube Shorts video URL',
  inputSchema: {
    type: 'object',
    properties: {
      url: {
        type: 'string',
        description: 'YouTube Shorts URL (format: https://www.youtube.com/shorts/VIDEO_ID)',
      },
    },
    required: ['url'],
    additionalProperties: false,
  },
};

// Register the tool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'extract_youtube_shorts_transcript') {
    const { url } = args;

    // Validate URL
    if (!url || !url.includes('youtube.com/shorts/')) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: false,
              transcript: '',
              segments: [],
              url: url || '',
              error: 'Invalid YouTube Shorts URL. Must be in format: https://www.youtube.com/shorts/VIDEO_ID',
            }, null, 2),
          },
        ],
      };
    }

    try {
      console.error(`[MCP Server] Extracting transcript from: ${url}`);

      // Call our extraction function
      const result = await extractYouTubeShortsTranscript(url);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      console.error(`[MCP Server] Error: ${error.message}`);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: false,
              transcript: '',
              segments: [],
              url: url,
              error: `Extraction failed: ${error.message}`,
            }, null, 2),
          },
        ],
      };
    }
  }

  // Unknown tool
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          success: false,
          error: `Unknown tool: ${name}`,
        }, null, 2),
      },
    ],
  };
});

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [extractTranscriptTool],
  };
});

// Start the server with stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[MCP Server] YouTube Shorts Transcript Extractor MCP server started');
  console.error('[MCP Server] Available tool: extract_youtube_shorts_transcript');
}

main().catch((error) => {
  console.error('[MCP Server] Fatal error:', error);
  process.exit(1);
});