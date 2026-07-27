(function(){
  var reportSubject = "Portal note: " + document.title;
  var reportBody = "Page: " + window.location.href + "\n\nWhat I noticed:\n";
  var reportHref = "mailto:707mike@gmail.com?subject=" + encodeURIComponent(reportSubject) + "&body=" + encodeURIComponent(reportBody);
  document.write(
    '<header style="display:flex; flex-wrap:wrap; gap:12px;">' +
    '<div style="display:flex; gap:16px; align-items:center; justify-content:center; width:100%; line-height:1;">' +
    '<a href="index.html" style="color:#d8c9a8; font-weight:normal; font-size:0.95rem; white-space:nowrap;">Cover</a>' +
    '<a href="fan.html" style="color:#f5e8c8; font-weight:bold; font-size:1.15rem; white-space:nowrap;">Fan</a>' +
    '<a href="tree.html" style="color:#f5e8c8; font-weight:bold; font-size:1.15rem; white-space:nowrap;">Tree</a>' +
    '<a href="surnames.html" style="color:#f5e8c8; font-weight:bold; font-size:1.15rem; white-space:nowrap;">Surnames</a>' +
    '<a href="names.html" style="color:#f5e8c8; font-weight:bold; font-size:1.15rem; white-space:nowrap;">Names</a>' +
    '</div>' +
    '<div style="text-align:center; width:100%; margin-top:6px;">' +
    '<a href="' + reportHref + '" style="color:#c8a96e; font-size:.78rem; letter-spacing:.04em; text-decoration:none; white-space:nowrap;">Report an error or suggest a correction</a>' +
    '</div>' +
    '</header>'
  );
})();
