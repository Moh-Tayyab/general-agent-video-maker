/**
 * AE_KaraokeAnimation.jsx
 *
 * Creates professional word-by-word karaoke captions in After Effects.
 * Each word drops in with:
 *   - Scale: 80% → 100% (ease-out, slight overshoot)
 *   - Position: drops from above (-20px Y offset)
 *   - Opacity: 0 → 100%
 *   - Anchor point: center
 *   - Timing: word starts animating 50ms BEFORE audio timestamp
 *
 * Usage:
 *   var captions = [
 *     { text: "SICK", start: 0.0, end: 2.0, highlight: false },
 *     { text: "WAIT", start: 4.5, end: 7.0, highlight: true },
 *   ];
 *   ae_karaoke_create(project, composition, captions, audioLayer);
 */

#target aftereffects

function ae_karaoke_create(project, comp, captions, audioLayer) {
  var fontSize = 96;
  var fontName = "Bangers";
  var fontColor = [1.0, 1.0, 1.0, 1.0];       // White
  var highlightColor = [1.0, 1.0, 0.0, 1.0];  // Yellow
  var strokeColor = [0.0, 0.0, 0.0, 1.0];     // Black
  var outlineWidth = 0.06;
  var positionOffsetY = -20;  // Drop from above
  var startScale = 80;
  var endScale = 100;
  var timingOffset = 0.05;  // 50ms before audio timestamp

  // Text layer for reference metrics
  var textLayer = comp.layers.addText();
  textLayer.name = "CaptionRef";
  var textProp = textLayer.property("Source Text");
  var docChar = textProp.value.documentFont;
  var docSize = textProp.value.fontSize;

  // Calculate word widths for centering
  function getWordWidth(word) {
    textProp.setValueAtTime(0, new TextDocument(word));
    return textProp.value.sourceRect.width;
  }

  function getLineWidth(words) {
    var total = 0;
    for (var i = 0; i < words.length; i++) {
      total += getWordWidth(words[i]);
      if (i < words.length - 1) total += getWordWidth(" ");
    }
    return total;
  }

  // Group captions into lines (~3-5 words per line for Shorts)
  var lines = [];
  var currentLine = { words: [], start: 0, end: 0, highlight: false };

  for (var i = 0; i < captions.length; i++) {
    var cap = captions[i];
    currentLine.words.push({ text: cap.text, start: cap.start, end: cap.end, highlight: cap.highlight });

    if (currentLine.words.length >= 4 || i === captions.length - 1) {
      currentLine.start = currentLine.words[0].start;
      currentLine.end = currentLine.words[currentLine.words.length - 1].end;
      // Check if any word is highlight
      for (var h = 0; h < currentLine.words.length; h++) {
        if (currentLine.words[h].highlight) {
          currentLine.highlight = true;
          break;
        }
      }
      lines.push(currentLine);
      currentLine = { words: [], start: 0, end: 0, highlight: false };
    }
  }

  // Create one shape layer per LINE (words positioned within)
  // Then animate each word's anchor/position within the line

  for (var l = 0; l < lines.length; l++) {
    var line = lines[l];
    var lineWords = line.words;
    var lineStart = line.start;
    var lineEnd = line.end;

    // Line container — group words visually
    var lineWidth = getLineWidth(lineWords.map(function(w) { return w.text; }));

    // Calculate baseline Y position (lower third of frame)
    var baselineY = comp.height * 0.75;

    // ===== SHAPE LAYER: word container with black outline backing =====
    var shapeLayer = comp.layers.addShape();
    shapeLayer.name = "Line_" + (l + 1);

    // Position: center X, baseline Y
    shapeLayer.position.setValueAtTime(lineStart - timingOffset, [comp.width / 2, baselineY]);

    // ===== TEXT LAYER: individual words with per-word animation =====
    var cumulativeX = -lineWidth / 2;  // Start from left edge of line

    for (var w = 0; w < lineWords.length; w++) {
      var word = lineWords[w];
      var wordText = word.text;
      var wordStart = word.start;
      var wordEnd = word.end;
      var isHighlight = word.highlight;
      var wordWidth = getWordWidth(wordText);

      // Word text layer
      var wordLayer = comp.layers.addText();
      wordLayer.name = wordText + "_" + (l + 1) + "_" + (w + 1);

      // Set text content
      var wordTextProp = wordLayer.property("Source Text");
      var td = new TextDocument(wordText);
      td.font = app.project.items[index].layers.addText().property("Source Text").value.font;
      td.fontSize = fontSize;
      td.font = fontName;
      td.fillColor = isHighlight ? highlightColor : fontColor;
      td.strokeColor = strokeColor;
      td.strokeWidth = outlineWidth;
      td.strokeFill = true;
      wordTextProp.setValueAtTime(0, td);

      // === ANCHOR POINT: move to center-bottom of word ===
      var wordRect = wordTextProp.value.sourceRect;
      var anchorX = wordWidth / 2;
      var anchorY = wordRect.height;  // bottom anchor
      wordLayer anchor.setValueAtTime(wordStart - timingOffset, [anchorX, anchorY]);

      // === POSITION: word drops in from above ===
      var wordCenterX = comp.width / 2 + cumulativeX + wordWidth / 2;

      // Start position: above (drop in from above)
      var startPosX = wordCenterX;
      var startPosY = baselineY + positionOffsetY;

      // End position: final resting place
      var endPosX = wordCenterX;
      var endPosY = baselineY;

      wordLayer.position.setValueAtTime(wordStart - timingOffset, [startPosX, startPosY]);
      wordLayer.position.setValueAtTime(wordStart, [endPosX, endPosY]);
      wordLayer.position.setValueAtTime(wordStart, [endPosX, endPosY], KeyframeInterpolationType.EASE_OUT);

      // === SCALE: 80% → 100% with ease-out ===
      var startScaleVal = [startScale, startScale, 100];
      var endScaleVal = [endScale, endScale, 100];

      wordLayer.scale.setValueAtTime(wordStart - timingOffset, startScaleVal);
      wordLayer.scale.setValueAtTime(wordStart, endScaleVal);
      wordLayer.scale.setValueAtTime(wordStart, endScaleVal, KeyframeInterpolationType.EASE_OUT);

      // === OPACITY: 0 → 100% with ease-in ===
      wordLayer.opacity.setValueAtTime(wordStart - timingOffset, 0);
      wordLayer.opacity.setValueAtTime(wordStart, 100);
      wordLayer.opacity.setValueAtTime(wordStart, 100, KeyframeInterpolationType.EASE_IN);

      cumulativeX += wordWidth + getWordWidth(" ");
    }
  }

  // Remove reference layer
  textLayer.remove();

  return lines.length;
}

/**
 * ae_karaoke_create_simple()
 * Simpler version: one text layer per word, each animated individually.
 * Better compatibility but more layers.
 */
function ae_karaoke_create_simple(project, comp, captions) {
  var fontSize = 96;
  var fontName = "Bangers";
  var fontColor = [1.0, 1.0, 1.0, 1.0];
  var highlightColor = [1.0, 1.0, 0.0, 1.0];
  var strokeColor = [0.0, 0.0, 0.0, 1.0];
  var outlineWidth = 0.06;
  var baselineY = comp.height * 0.75;
  var startScale = 80;
  var timingOffset = 0.05;

  var result = {};

  for (var i = 0; i < captions.length; i++) {
    var cap = captions[i];
    var isHighlight = !!cap.highlight;

    // Create text layer for this word
    var wordLayer = comp.layers.addText();
    wordLayer.name = "W_" + i + "_" + cap.text.replace(/\s+/g, "_");

    // Set text
    var textProp = wordLayer.property("Source Text");
    var td = new TextDocument(cap.text);
    td.fontSize = fontSize;
    td.font = fontName;
    td.fillColor = isHighlight ? highlightColor : fontColor;
    td.strokeColor = strokeColor;
    td.strokeWidth = outlineWidth;
    td.strokeFill = true;
    td.justify = TextJustification.CENTER;
    textProp.setValueAtTime(0, td);

    // Get word width for centering
    var wordWidth = textProp.value.sourceRect.width;

    // Position: center X, lower third Y
    var wordCenterX = comp.width / 2 - wordWidth / 2;
    var wordStartX = wordCenterX;
    var wordStartY = baselineY + 20;  // Drop from above

    wordLayer.position.setValueAtTime(cap.start - timingOffset, [wordStartX, wordStartY]);
    wordLayer.position.setValueAtTime(cap.start, [wordCenterX, baselineY]);
    wordLayer.position.setValueAtTime(cap.start, [wordCenterX, baselineY], KeyframeInterpolationType.EASE_OUT);

    // Scale: 80 → 100
    wordLayer.scale.setValueAtTime(cap.start - timingOffset, [startScale, startScale, 100]);
    wordLayer.scale.setValueAtTime(cap.start, [100, 100, 100]);
    wordLayer.scale.setValueAtTime(cap.start, [100, 100, 100], KeyframeInterpolationType.EASE_OUT);

    // Opacity: 0 → 100
    wordLayer.opacity.setValueAtTime(cap.start - timingOffset, 0);
    wordLayer.opacity.setValueAtTime(cap.start, 100);

    result[cap.text] = wordLayer.name;
  }

  return result;
}

// Export for use by MCP server
$.global.ae_karaoke_create = ae_karaoke_create;
$.global.ae_karaoke_create_simple = ae_karaoke_create_simple;