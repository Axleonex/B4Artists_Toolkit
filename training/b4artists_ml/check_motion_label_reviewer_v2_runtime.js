"use strict";

// Execute the generated page's own completion/export functions against a
// minimal local DOM. This is a contract fixture, not a visual browser result.
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const root = __dirname;
const htmlPath = path.join(root, "results", "motion-label-reviewer-v2", "reviewer.html");
const source = fs.readFileSync(htmlPath, "utf8");
const match = source.match(/<script>([\s\S]*)<\/script>/);
if (!match) throw new Error("Generated reviewer script is missing");

const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      id,
      value: "",
      checked: false,
      disabled: false,
      textContent: "",
      classList: { toggle() {} },
      click() {},
    });
  }
  return elements.get(id);
}
const buttons = ["accepted", "rejected", "uncertain"].map((value) => ({
  dataset: { v: value },
  classList: { toggle() {} },
  onclick: null,
}));
const context = {
  console,
  Blob,
  URL,
  Date,
  JSON,
  Number,
  String,
  Math,
  setTimeout,
  setInterval: () => 1,
  clearInterval() {},
  localStorage: { getItem: () => "{corrupt saved state", setItem() {} },
  document: {
    getElementById(id) {
      const value = element(id);
      if (id === "view") {
        value.getContext = () => ({
          clearRect() {}, fillText() {}, beginPath() {}, moveTo() {}, lineTo() {},
          stroke() {}, arc() {}, fill() {},
        });
      }
      return value;
    },
    querySelectorAll: () => buttons,
    createElement: () => ({ click() {} }),
  },
};
vm.createContext(context);
vm.runInContext(match[1], context, { filename: "reviewer.html" });
const result = vm.runInContext(`(() => {
  const sample = items[0];
  const missingIdRejected = !validReview(sample, {
    verdict: 'accepted', corrected_start: sample.start, corrected_end: sample.end,
    intent: 'unknown', notes: '', reviewed_utc: new Date().toISOString()
  });
  const missingTimestampRejected = !validReview(sample, {
    review_id: sample.review_id, verdict: 'accepted', corrected_start: sample.start,
    corrected_end: sample.end, intent: 'unknown', notes: ''
  });
  const stringFramesRejected = !validReview(sample, {
    review_id: sample.review_id, verdict: 'accepted', corrected_start: String(sample.start),
    corrected_end: String(sample.end), intent: 'unknown', notes: '',
    reviewed_utc: new Date().toISOString()
  });
  const futureTimestampRejected = !validReview(sample, {
    review_id: sample.review_id, verdict: 'accepted', corrected_start: sample.start,
    corrected_end: sample.end, intent: 'unknown', notes: '',
    reviewed_utc: '2999-01-01T00:00:00Z'
  });
  const validSessionStarted = sessionStarted;
  sessionStarted = 'invalid';
  const invalidSessionRejected = !validReview(sample, {
    review_id: sample.review_id, verdict: 'accepted', corrected_start: sample.start,
    corrected_end: sample.end, intent: 'unknown', notes: '',
    reviewed_utc: new Date().toISOString()
  });
  sessionStarted = validSessionStarted;
  $('reviewer').value = 'x'.repeat(81);
  $('experience').value = '5_plus_years';
  $('independent').checked = true;
  const overlongReviewerRejected = !validReviewer();
  $('reviewer').value = 'synthetic-contract-fixture';
  $('experience').value = '5_plus_years';
  $('independent').checked = true;
  reviews = {};
  for (const item of items) {
    reviews[item.review_id] = {
      review_id: item.review_id, verdict: 'uncertain', corrected_start: item.start,
      corrected_end: item.end, intent: 'unknown', notes: 'synthetic contract fixture',
      reviewed_utc: new Date().toISOString()
    };
  }
  let captured = null;
  download = (name, value) => { captured = {name, value}; };
  render();
  const exportEnabled = !$('export').disabled;
  exportComplete();
  return {missingIdRejected, missingTimestampRejected, stringFramesRejected,
          futureTimestampRejected, invalidSessionRejected, overlongReviewerRejected,
          corruptSavedStateRecovered: items.length === 130, exportEnabled,
          notice: $('notice').textContent, captured};
})()`, context);
process.stdout.write(JSON.stringify(result));
