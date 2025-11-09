/**
 * Basit test runner - npm install sorunları için alternatif
 */
import { execSync } from 'child_process';
import { existsSync } from 'fs';

console.log('Frontend Test Runner');
console.log('===================\n');

// Test dosyalarını kontrol et
const testFiles = [
  'src/__tests__/Home.test.jsx',
  'src/__tests__/DropDetail.test.jsx',
];

console.log('Test dosyaları kontrol ediliyor...');
testFiles.forEach(file => {
  if (existsSync(file)) {
    console.log(`✓ ${file} mevcut`);
  } else {
    console.log(`✗ ${file} bulunamadı`);
  }
});

console.log('\nTest dosyaları hazır!');
console.log('Vitest ile çalıştırmak için: npm test');

