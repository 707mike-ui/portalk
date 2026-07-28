const fs = require('fs');
const txt = fs.readFileSync('/Users/admin/Desktop/portalk/data.js','utf8');
const m = txt.match(/const TREE\s*=\s*(\{.*\});?\s*$/s);
const raw = m[1].replace(/individuals:/,'"individuals":').replace(/families:/,'"families":');
const tree = JSON.parse(raw);
const surnames = new Set();
Object.values(tree.individuals).forEach(function(rec){
  if (rec.page === undefined || rec.page === null || rec.page === false) return;
  var parts = rec.name.trim().split(' ');
  if (parts.length < 2) return;
  surnames.add(parts[parts.length-1]);
});
console.log([...surnames].sort().join('\n'));
