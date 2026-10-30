// Render scene.html frame-by-frame with Playwright and pipe JPEGs into ffmpeg.
// usage: node render.js <workdir> <w> <h> <out.mp4>            full video
//        node render.js <workdir> <w> <h> <prefix> t1,t2,...   still previews (PNG)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const [work, w, h, out, stills] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync(path.join(work, 'timeline.json'), 'utf8'));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h } });
  page.on('console', m => console.log('page:', m.text()));
  page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  await page.goto('file://' + path.join(__dirname, `scene.html?w=${w}&h=${h}`));
  await page.evaluate(async (tl) => { window.setTimeline(tl); await window.ready; }, tl);
  const grab = (t, type) => page.evaluate(([t, type]) => { window.renderFrame(t); return document.getElementById('c').toDataURL(type, 0.93); }, [t, type]);
  if (stills) {
    for (const t of stills.split(',').map(Number)) {
      const url = await grab(t, 'image/png');
      fs.writeFileSync(`${out}_${t.toFixed(1)}.png`, Buffer.from(url.split(',')[1], 'base64'));
    }
    await browser.close(); return;
  }
  const fps = tl.fps, n = Math.ceil(tl.total * fps);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(work, 'mix.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    const url = await grab(i / fps, 'image/jpeg');
    const buf = Buffer.from(url.split(',')[1], 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`${w}x${h} frame ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote', out);
})();
