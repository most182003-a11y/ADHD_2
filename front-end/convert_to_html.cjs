const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const hljs = require('highlight.js');

// Configure marked with syntax highlighting
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (e) {}
    }
    return code;
  },
  breaks: false,
  gfm: true,
});

// Read markdown file
const mdPath = path.join(__dirname, '..', 'book', 'revised_book.md');
const mdContent = fs.readFileSync(mdPath, 'utf8');

// Convert to HTML
let htmlContent = marked.parse(mdContent);

// Fix page-break divs
htmlContent = htmlContent.replace(/<div style="page-break-before: always;"><\/div>/g, '<div class="page-break"></div>');

// Full HTML template with print CSS
const fullHtml = `<!DOCTYPE html>
<html dir="ltr">
<head>
<meta charset="utf-8">
<title>ADHD Progress Insights - Graduation Project Book</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
<style>
  @page {
    size: A4;
    margin: 30mm 25mm 30mm 25mm;
  }

  * { box-sizing: border-box; }

  body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 12pt;
    line-height: 2.0;
    color: #1a1a1a;
    counter-reset: chapter;
  }

  h1 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 22pt;
    color: #1e3a5f;
    margin-top: 40px;
    margin-bottom: 25px;
    page-break-before: always;
    page-break-after: avoid;
    border-bottom: 3px solid #1e3a5f;
    padding-bottom: 12px;
  }

  h1:first-of-type { page-break-before: avoid; }

  h2 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 17pt;
    color: #2c5282;
    margin-top: 35px;
    margin-bottom: 15px;
    page-break-after: avoid;
  }

  h3 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 14pt;
    color: #2d3748;
    margin-top: 28px;
    margin-bottom: 12px;
    page-break-after: avoid;
  }

  h4 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 12pt;
    color: #4a5568;
    margin-top: 20px;
    margin-bottom: 10px;
  }

  p { margin: 12px 0; text-align: justify; }

  ul, ol { margin: 12px 0; padding-left: 30px; }
  li { margin: 6px 0; }

  code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    background-color: #f7f8fa;
    padding: 2px 6px;
    border-radius: 3px;
    color: #c7254e;
  }

  pre {
    background-color: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 16px 20px;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 16px 0;
  }

  pre code {
    background: none;
    padding: 0;
    font-size: 9pt;
    color: #24292e;
    line-height: 1.6;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 11pt;
    page-break-inside: avoid;
  }

  th, td {
    border: 1px solid #d1d5db;
    padding: 10px 14px;
    text-align: left;
    vertical-align: top;
  }

  th {
    background-color: #1e3a5f;
    color: white;
    font-weight: bold;
  }

  tr:nth-child(even) { background-color: #f9fafb; }

  blockquote {
    border-left: 5px solid #1e3a5f;
    margin: 20px 0;
    padding: 15px 20px;
    background-color: #f0f4f8;
    font-style: italic;
  }

  strong { color: #1a1a1a; }

  hr {
    border: none;
    border-top: 2px solid #e2e8f0;
    margin: 35px 0;
  }

  .page-break { page-break-before: always; }

  /* Cover page styling */
  .cover-page {
    page-break-after: always;
    text-align: center;
    padding-top: 140px;
  }

  .cover-page h1 {
    font-size: 30pt;
    border: none;
    color: #1e3a5f;
    margin-bottom: 15px;
  }

  .cover-page .subtitle {
    font-size: 18pt;
    color: #4a5568;
    margin-bottom: 60px;
  }

  .cover-page .meta {
    font-size: 13pt;
    color: #718096;
    margin-top: 80px;
    line-height: 2.2;
  }

  .cover-page .line { border-top: 2px solid #1e3a5f; width: 200px; margin: 40px auto; }

  /* TOC styling */
  .toc { page-break-after: always; }
  .toc h1 { page-break-before: avoid; text-align: center; border: none; }
  .toc ul { list-style: none; padding: 0; }
  .toc li { margin: 8px 0; font-size: 12pt; }
  .toc a { color: #1e3a5f; text-decoration: none; }
  .toc .chapter { font-weight: bold; }

  /* Print optimization */
  @media print {
    a { color: #1a1a1a; text-decoration: none; }
    pre { white-space: pre-wrap; }
    img { max-width: 100%; }
    p { orphans: 3; widows: 3; }
  }
</style>
</head>
<body>

${htmlContent}

</body>
</html>`;

// Write HTML file
const htmlPath = path.join(__dirname, '..', 'book', 'complete_book.html');
fs.writeFileSync(htmlPath, fullHtml, 'utf8');

console.log('HTML file generated successfully:', htmlPath);
console.log('File size:', (fs.statSync(htmlPath).size / 1024).toFixed(1), 'KB');
