import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

(async () => {
  const htmlPath = path.resolve(__dirname, '..', 'book', 'complete_book.html');
  const pdfPath = path.resolve(__dirname, '..', 'book', 'ADHD_Progress_Insights_Book.pdf');

  console.log('Launching headless browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();

  // Set viewport to simulate A4 width at 96 DPI
  await page.setViewport({
    width: 1200,
    height: 1600,
  });

  // Load the HTML file
  await page.goto(`file://${htmlPath}`, {
    waitUntil: 'networkidle0',
    timeout: 60000,
  });

  // Wait a bit for fonts and rendering
  await new Promise(r => setTimeout(r, 2000));

  console.log('Generating PDF...');

  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: {
      top: '20mm',
      bottom: '20mm',
      left: '20mm',
      right: '20mm',
    },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:8pt; color:#999; text-align:center; width:100%; padding-top:5mm;"><i>ADHD Progress Insights - Graduation Project</i></div>',
    footerTemplate: `
      <div style="width:100%; text-align:center; font-size:8pt; color:#666; padding:3mm 20mm;">
        <span class="pageNumber"></span>
      </div>
    `,
    preferCSSPageSize: true,
  });

  await browser.close();

  const stats = fs.statSync(pdfPath);
  console.log(`PDF generated successfully: ${pdfPath}`);
  console.log(`File size: ${(stats.size / 1024).toFixed(1)} KB`);

  // Count approximate pages by reading PDF
  const content = fs.readFileSync(pdfPath, 'utf8');
  const pageCount = (content.match(/\/Type\s*\/Page[^s]/g) || []).length;
  console.log(`Actual page count: ${pageCount}`);

})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
