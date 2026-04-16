/**
 * AE_LinearWipe.jsx
 *
 * Creates a linear wipe transition between two clips.
 * Uses AE's standard Wipe effect with custom orientation and edge softness.
 *
 * direction: "left" | "right" | "top" | "bottom"
 * softness: 0.0 - 1.0 (edge softness percentage)
 */
#target aftereffects

function ae_linear_wipe(clipA, clipB, comp, params) {
  var direction = params.direction || "left";
  var transitionDuration = params.duration || 1.0;
  var softness = params.softness || 0.0;
  var clipA_start = params.clipA_start || 0;
  var clipB_start = params.clipB_start || 0;

  // Place clip A on V1
  var layerA = comp.layers.add(clipA);
  layerA.startTime = clipA_start;

  // Place clip B on V2 (above A)
  var layerB = comp.layers.add(clipB);
  layerB.startTime = clipB_start;
  layerB.moveAfter(layerA);

  // Calculate transition start time (clip A ends - duration)
  var transitionStart = clipA_start + (layerA.source.duration - transitionDuration);

  // Apply Wipe effect to layer B
  var wipeEffect = layerB.property("Effects").addProperty("ADBE Wipe");
  var transitionAngle = 0;

  if (direction === "left") transitionAngle = 0;
  else if (direction === "right") transitionAngle = 180;
  else if (direction === "top") transitionAngle = 270;
  else if (direction === "bottom") transitionAngle = 90;

  // Set wipe parameters
  wipeEffect.property("Transition Completion").setValueAtTime(transitionStart, 0);
  wipeEffect.property("Transition Completion").setValueAtTime(
    transitionStart + transitionDuration,
    100,
    KeyframeInterpolationType.EASE_IN_OUT
  );
  wipeEffect.property("Edge Feather").setValueAtTime(transitionStart, softness * 5);

  return {
    layerA: layerA.name,
    layerB: layerB.name,
    transitionStart: transitionStart,
    transitionDuration: transitionDuration
  };
}

/**
 * ae_color_grade_lumetri()
 * Apply Lumetri Color effect to a layer.
 * preset: "cinematic" | "bright" | "vibrant" | "muted"
 */
function ae_color_grade_lumetri(layer, params) {
  var preset = params.preset || "cinematic";
  var intensity = params.intensity || 0.8;

  var lumetri = layer.property("Effects").addProperty("ADBE Lumetri");

  if (preset === "cinematic") {
    lumetri.property("adows").setValueAtTime(0, 0);
    lumetri.property("hi-lights").setValueAtTime(0, -10);
    lumetri.property("blacks").setValueAtTime(0, -5);
    lumetri.property("whites").setValueAtTime(0, 5);
    lumetri.property("saturation").setValueAtTime(0, -5);
  } else if (preset === "bright") {
    lumetri.property("blacks").setValueAtTime(0, 20);
    lumetri.property("whites").setValueAtTime(0, 10);
    lumetri.property("saturation").setValueAtTime(0, 5);
  } else if (preset === "vibrant") {
    lumetri.property("saturation").setValueAtTime(0, 20);
    lumetri.property("hi-lights").setValueAtTime(0, 5);
  } else if (preset === "muted") {
    lumetri.property("saturation").setValueAtTime(0, -15);
    lumetri.property("contrasts").setValueAtTime(0, 10);
  }

  lumetri.property("Intensity").setValueAtTime(0, intensity * 100);

  return lumetri.name;
}

/**
 * ae_add_text_preset()
 * Add a styled text layer with the Maven-Edit look.
 */
function ae_add_text_preset(comp, text, params) {
  var fontSize = params.fontSize || 96;
  var fontName = params.fontName || "Bangers";
  var fontColor = params.fontColor || [1.0, 1.0, 1.0, 1.0];
  var position = params.position || [comp.width / 2, comp.height * 0.75];
  var startTime = params.startTime || 0;
  var endTime = params.endTime || startTime + 2;

  var textLayer = comp.layers.addText();
  textLayer.name = "T_" + text.replace(/\s+/g, "_").substring(0, 10);

  var textProp = textLayer.property("Source Text");
  var td = new TextDocument(text);
  td.fontSize = fontSize;
  td.font = fontName;
  td.fillColor = fontColor;
  td.strokeColor = [0, 0, 0, 1];
  td.strokeWidth = 0.06;
  td.strokeFill = true;
  td.justify = TextJustification.CENTER;
  textProp.setValueAtTime(0, td);

  textLayer.position.setValueAtTime(startTime, position);
  textLayer.opacity.setValueAtTime(startTime, 100);
  textLayer.opacity.setValueAtTime(endTime - 0.1, 100);
  textLayer.opacity.setValueAtTime(endTime, 0);

  return textLayer.name;
}

$.global.ae_linear_wipe = ae_linear_wipe;
$.global.ae_color_grade_lumetri = ae_color_grade_lumetri;
$.global.ae_add_text_preset = ae_add_text_preset;