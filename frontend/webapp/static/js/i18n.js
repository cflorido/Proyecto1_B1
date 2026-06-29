const translations = {
  en: {
    "nav.classify_one": "Classify One",
    "nav.classify_file": "Classify File",
    "nav.retrain": "Retrain Model",
    "home.title": "Detecting Fake News",
    "home.subtitle": "Ensuring reliable information",
    "home.description": "This app uses a Gradient Boosting classifier to detect fake political news. Users can submit articles or upload CSV files for batch classification.",
    "home.keywords": "Keywords",
    "home.true_title": "Most common words in Titles",
    "home.true_body": "Most common words in Bodies",
    "classify.title": "Classifier",
    "classify.instructions": "Instructions",
    "classify.follow_steps": "Please follow these steps to classify the article:",
    "classify.step_title": "Enter the article title.",
    "classify.step_body": "Enter the full article body.",
    "classify.step_click": "Click the \"Classify\" button to get results.",
    "classify.button": "Classify",
    "classify.enter": "Enter",
    "classify.field_id": "Article ID",
    "classify.field_date": "Article Date",
    "classify.field_title": "Title",
    "classify.field_body": "Body",
    "classify.results": "Classification Results",
    "classify.title_label": "Title:",
    "classify.body_label": "Body:",
    "classify.class_label": "Classification:",
    "classify.prob_true": "Probability True",
    "classify.prob_false": "Probability False",
    "file.title": "File Classifier",
    "file.instructions": "Instructions",
    "file.follow_steps": "Upload a CSV with the required columns.",
    "file.step_csv": "Select a CSV file from your device.",
    "file.step_columns": "Ensure CSV contains required columns.",
    "file.step_upload": "Click upload to process the file.",
    "file.upload": "Upload File",
    "file.select": "Select a file:",
    "file.button": "Upload and Classify",
    "file.results": "Classification Results",
    "file.col_title": "Title",
    "file.col_body": "Body",
    "file.col_class": "Classification",
    "file.col_prob_true": "Prob True",
    "file.col_prob_false": "Prob False",
    "retrain.title": "Retrain",
    "retrain.instructions": "Instructions",
    "retrain.follow_steps": "Upload a labeled CSV to retrain the model.",
    "retrain.step_csv": "Select a CSV file from your device.",
    "retrain.step_columns": "Ensure CSV has columns: ID, Label, Titulo, Descripcion, Fecha.",
    "retrain.step_upload": "Click to start retraining.",
    "retrain.upload": "Upload File",
    "retrain.select": "Select a file:",
    "retrain.button": "Retrain",
    "retrain.results": "Retraining Results",
    "retrain.train_metrics": "Training Metrics",
    "retrain.val_metrics": "Validation Metrics",
    "retrain.recall": "Recall",
    "retrain.precision": "Precision",
    "retrain.accuracy": "Accuracy",
    "processing.title": "Processing request",
    "processing.default": "We are analyzing the information. This can take a few seconds.",
    "processing.classify": "Classifying article, please wait...",
    "processing.classify_file": "Classifying file, please wait...",
    "processing.retrain": "Retraining model, please wait..."
  },
  es: {}
};

function detectBrowserLang() {
  const lang = navigator.language || navigator.userLanguage || 'es';
  return lang.startsWith('en') ? 'en' : 'es';
}

function setLanguage(lang) {
  if (!translations[lang]) lang = 'es';
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const txt = translations[lang][key];
    if (txt) {
      if (el.placeholder !== undefined && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA')) {
        el.placeholder = txt;
      } else {
        el.textContent = txt;
      }
    }
  });
  // Persist selection
  try { localStorage.setItem('lang', lang); } catch (e) {}
}

function showProcessingOverlay(messageKey) {
  const overlay = document.getElementById('processing-overlay');
  const messageEl = document.getElementById('processing-message');
  if (!overlay || !messageEl) return;

  const lang = localStorage.getItem('lang') || detectBrowserLang();
  const message = translations[lang] && translations[lang][messageKey]
    ? translations[lang][messageKey]
    : null;

  if (message) {
    messageEl.textContent = message;
  }

  overlay.classList.remove('d-none');
}

function wireProcessingForms() {
  document.querySelectorAll('.js-processing-form').forEach(form => {
    form.addEventListener('submit', () => {
      const messageKey = form.getAttribute('data-loading-key') || 'processing.default';
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.setAttribute('disabled', 'disabled');
      }
      showProcessingOverlay(messageKey);
    });
  });
}

// Load language on start
document.addEventListener('DOMContentLoaded', () => {
  const stored = localStorage.getItem('lang');
  const lang = stored || detectBrowserLang();
  const selector = document.getElementById('lang-select');
  if (selector) selector.value = lang;
  setLanguage(lang);
  wireProcessingForms();
});
