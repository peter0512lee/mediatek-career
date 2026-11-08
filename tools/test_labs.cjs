const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
// The pure decoder can be checked without a browser; UI is verified separately.
const scope = { document: { getElementById: () => null } };
vm.createContext(scope);
vm.runInContext(fs.readFileSync('assets/labs.js', 'utf8'), scope);
const decode = scope.decodeHex;
const sample = '4c 47 01 02 02 00 01 00 01 00 00 00 e8 03 00 00 34 12';
assert.match(decode(sample), /value=4660/);
assert.match(decode(sample), /timestamp_ms = 1000/);
assert.match(decode(sample.slice(0, -3)), /NEED_MORE/);
assert.match(decode('4c'), /NEED_MORE/);
assert.match(decode('0xz'), /輸入錯誤/);
assert.match(decode(sample.replace('4c 47 01', '4c 47 02')), /INVALID/);
assert.match(decode(sample.replace('02 00 01 00', '21 00 01 00')), /INVALID/);
assert.match(decode(sample + ' 00'), /剩餘 1 bytes/);
assert.match(decode(sample.replace('02 00 01 00', '02 00 63 00')), /UNKNOWN payload=3412/);
console.log('browser decoder logic: PASS');
