const http = require('http');
const url = require('url');
const { exec } = require('child_process');

http.createServer((req, res) => {
  const query = url.parse(req.url, true).query;


  exec("ls " + query.dir, (err, stdout, stderr) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    if (err) {
      res.end("Error occurred");
      return;
    }

    res.end("<pre>" + stdout + "</pre>");
  });
}).listen(3000);
