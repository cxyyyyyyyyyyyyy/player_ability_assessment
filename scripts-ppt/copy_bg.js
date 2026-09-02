const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const src = path.join(root, 'background photo.jpg');
const imgDir = path.join(root, 'frontend', 'img');
const dst = path.join(imgDir, 'background.jpg');

fs.mkdirSync(imgDir, { recursive: true });
fs.copyFileSync(src, dst);
console.log('OK ->', dst);
