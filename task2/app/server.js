const express = require("express");
const _ = require("lodash");

const app = express();
app.use(express.json());

// Intentionally simplistic usage to ensure lodash is included in runtime deps.
app.post("/merge", (req, res) => {
  const base = { safe: true };
  const merged = _.merge(base, req.body);
  res.json({ ok: true, merged });
});

app.get("/healthz", (_req, res) => res.status(200).send("ok"));

const port = process.env.PORT || 3000;
app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`listening on ${port}`);
});

