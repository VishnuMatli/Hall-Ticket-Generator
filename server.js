// server.js - FINAL with security + traffic control + connection logging + city/GPS location
const express = require("express");
const path = require("path");
const fs = require("fs");
const bodyParser = require("body-parser");
const multer = require("multer");
const ejs = require("ejs");
const mysql = require("mysql2");
const puppeteer = require("puppeteer");
const geoip = require("geoip-lite");
const https = require("https"); // <-- added for reverse geocode
const Razorpay = require("razorpay");
const crypto = require("crypto");
const QRCode = require("qrcode");

const app = express();
app.set("trust proxy", true);

// ---------- CONFIG ----------
const UPLOADS_DIR = path.join(__dirname, "uploads");
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

// ---------- MYSQL CONNECTION ----------
require("dotenv").config();
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASS, // your DB password
  database: process.env.DB_NAME,
  dateStrings: true, // avoid timezone shifting for DATE
});

db.connect((err) => {
  if (err) console.error("DB connection error:", err);
  else console.log("Connected to MySQL:", process.env.DB_NAME);
});

// ---------- RAZORPAY CLIENT (TEST / LIVE VIA ENV) ----------
const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID || "",
  key_secret: process.env.RAZORPAY_KEY_SECRET || "",
});

// ---------- VIEW ENGINE ----------
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// ---------- MIDDLEWARES ----------
app.use(express.static(path.join(__dirname, "public")));
app.use("/uploads", express.static(UPLOADS_DIR));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// small logger
app.use((req, res, next) => {
  console.log(new Date().toISOString(), req.method, req.url);
  next();
});

// ---------- SECURITY / UTILS ----------

// Only allow real JPEG/PNG by magic bytes (not just extension)
function isSafeImage(buffer) {
  if (!buffer || buffer.length < 4) return false;
  const sig = buffer.toString("hex", 0, 4);
  // JPEG starts with ffd8, PNG with 89504e47
  return sig.startsWith("ffd8") || sig.startsWith("89504e47");
}

// Traffic delay middleware: add ~3s delay on busy routes
function trafficDelay(req, res, next) {
  setTimeout(next, 50); // 3 seconds
}

// Get client IP
function getClientIp(req) {
  const xfwd = req.headers["x-forwarded-for"];
  if (xfwd) {
    return xfwd.split(",")[0].trim();
  }
  return req.socket?.remoteAddress || "Unknown IP";
}

// Device name = user-agent
const UAParser = require("ua-parser-js");

function getDeviceName(req) {
  const uaString = req.headers["user-agent"] || "";
  const parser = new UAParser(uaString);
  const result = parser.getResult();

  const os = result.os?.name ? `${result.os.name} ${result.os.version || ""}` : "Unknown OS";
  const device =
    result.device?.vendor || result.device?.model
      ? `${result.device.vendor || ""} ${result.device.model || ""}`.trim()
      : "PC / Laptop";

  const browser = result.browser?.name || "Unknown Browser";

  return `${os} – ${device} (${browser})`;
}

// Reverse geocode GPS (lat,lon) → area name using OpenStreetMap
function reverseGeo(lat, lon) {
  return new Promise((resolve) => {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
    https
      .get(
        url,
        { headers: { "User-Agent": "MITS-HallTicket-System" } },
        (resp) => {
          let data = "";
          resp.on("data", (chunk) => (data += chunk));
          resp.on("end", () => {
            try {
              const json = JSON.parse(data);
              if (json && json.address) {
                const area =
                  json.address.city ||
                  json.address.town ||
                  json.address.village ||
                  json.address.suburb ||
                  json.address.state ||
                  json.address.county;
                resolve(area || "Unknown");
              } else {
                resolve("Unknown");
              }
            } catch (e) {
              console.error("Reverse geo parse error:", e);
              resolve("Unknown");
            }
          });
        }
      )
      .on("error", (e) => {
        console.error("Reverse geo HTTP error:", e);
        resolve("Unknown");
      });
  });
}

// Decide final location: GPS (if provided) OR city from geoip OR fallback with IP
async function resolveLocation(req, device_gps) {
  // 1) If browser sent GPS and it looks valid, try to convert to area name
  if (
    device_gps &&
    device_gps !== "Permission Denied" &&
    device_gps !== "Unknown"
  ) {
    if (device_gps.includes(",")) {
      const [latStr, lonStr] = device_gps.split(",");
      const lat = parseFloat(latStr.trim());
      const lon = parseFloat(lonStr.trim());
      if (!isNaN(lat) && !isNaN(lon)) {
        const area = await reverseGeo(lat, lon);
        if (area && area !== "Unknown") {
          return area; // store area name instead of raw lat,long
        }
      }
    }
  }

  // 2) Fallback to IP → city lookup
  let ip = getClientIp(req);
  ip = ip.replace("::ffff:", "");

  try {
    const geo = geoip.lookup(ip);
    if (geo) {
      // e.g. { country: 'IN', region: 'AP', city: 'Madanapalle', ... }
      const parts = [];
      if (geo.city) parts.push(geo.city);
      if (geo.region) parts.push(geo.region);
      if (geo.country) parts.push(geo.country);
      if (parts.length > 0) return parts.join(", ");
    }
  } catch (e) {
    console.error("GeoIP lookup failed:", e);
  }

  // 3) Last fallback: unknown with IP
  return `Unknown (${ip || "no-ip"})`;
}

// Store connection log into DB
async function logConnection(req, { roll_number, name, semester, hallticketInfo }) {
  const ip = req.headers["x-forwarded-for"]
    ? req.headers["x-forwarded-for"].split(",")[0].trim()
    : req.socket?.remoteAddress?.replace("::ffff:", "") || "Unknown IP";

  const device = getDeviceName(req);

  const sql = `
    INSERT INTO connection_logs
      (ip_address, device_name, roll_number, name, semester, hallticket_info)
    VALUES (?, ?, ?, ?, ?, ?)
  `;

  const params = [
    ip,
    device,
    roll_number || "",
    name || "",
    semester || "",
    hallticketInfo || "",
  ];

  db.query(sql, params, (err) => {
    if (err) console.error("Error logging connection:", err);
  });
}


app.use("/api", trafficDelay);
app.use("/generate-halltkt", trafficDelay);

// ---------- MULTER (TEMP FILE UPLOAD) ----------
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) =>
    cb(
      null,
      "tmp-" +
        Date.now() +
        (file.originalname ? path.extname(file.originalname) : ".jpg")
    ),
});
const upload = multer({
  storage,
  // Basic MIME filter as first line of defense
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.startsWith("image/")) {
      return cb(new Error("Only image uploads are allowed."));
    }
    cb(null, true);
  },
});

// ---------- ROUTES ----------

// Create Razorpay order for exam fee payment
// Helper to compute exam fee based on rules and backlog count.
// sem_exam_fees.amount / exam_fee_rules.amount are stored in rupees; Razorpay expects paise.
function computeExamFee(roll_number, exam_type, mode, semester, cb) {
  const safeMode = (mode || "Autonomous").trim();
  const safeSem = (semester || "").trim();
  const lowerType = (exam_type || "").toLowerCase();

  // Helper: fallback to legacy exam_fee_rules table
  function fallbackRegular() {
    const backlogs = 0;
    db.query(
      "SELECT amount FROM exam_fee_rules WHERE exam_type=? AND ? BETWEEN min_backlogs AND max_backlogs ORDER BY id LIMIT 1",
      [exam_type, backlogs],
      (err, rows) => {
        if (err) {
          console.error("exam_fee_rules query error (regular):", err);
          return cb(null, 1500 * 100); // default 1500 INR
        }
        if (!rows || !rows.length) return cb(null, 1500 * 100);
        return cb(null, Number(rows[0].amount) * 100);
      }
    );
  }

  function fallbackSupp(backlogCount) {
    db.query(
      "SELECT amount FROM exam_fee_rules WHERE exam_type=? AND ? BETWEEN min_backlogs AND max_backlogs ORDER BY id LIMIT 1",
      [exam_type, backlogCount],
      (rerr, rows) => {
        if (rerr) {
          console.error("exam_fee_rules query error (supp):", rerr);
          return cb(null, 600 * 100);
        }
        if (!rows || !rows.length) return cb(null, 600 * 100);
        return cb(null, Number(rows[0].amount) * 100);
      }
    );
  }

  // Regular exams: prefer sem_exam_fees by mode + semester
  if (lowerType === "regular") {
    const params = [safeMode, exam_type, 0];
    let sql =
      "SELECT amount FROM sem_exam_fees WHERE mode=? AND exam_type=? AND ? BETWEEN min_backlogs AND max_backlogs";
    if (safeSem) {
      sql += " AND (semester=? OR semester='ALL')";
      params.push(safeSem);
    }
    sql += " ORDER BY semester='ALL' ASC, min_backlogs ASC LIMIT 1";

    return db.query(sql, params, (err, rows) => {
      if (err) {
        console.error("sem_exam_fees query error (regular):", err);
        return fallbackRegular();
      }
      if (!rows || !rows.length) {
        return fallbackRegular();
      }
      return cb(null, Number(rows[0].amount) * 100);
    });
  }

  // Supplementary: count backlogs and pick matching slab; prefer sem_exam_fees
  db.query(
    "SELECT COUNT(*) AS c FROM student_backlogs WHERE roll_number=?",
    [roll_number],
    (cerr, crows) => {
      if (cerr) {
        console.error("Backlog count error:", cerr);
        return cb(null, 600 * 100); // fallback 600 INR
      }
      const count = crows && crows[0] ? crows[0].c : 0;

      const params = [safeMode, exam_type, count];
      let sql =
        "SELECT amount FROM sem_exam_fees WHERE mode=? AND exam_type=? AND ? BETWEEN min_backlogs AND max_backlogs";
      if (safeSem) {
        sql += " AND (semester=? OR semester='ALL')";
        params.push(safeSem);
      }
      sql += " ORDER BY semester='ALL' ASC, min_backlogs ASC LIMIT 1";

      db.query(sql, params, (rerr, rows) => {
        if (rerr) {
          console.error("sem_exam_fees query error (supp):", rerr);
          return fallbackSupp(count);
        }
        if (!rows || !rows.length) {
          return fallbackSupp(count);
        }
        return cb(null, Number(rows[0].amount) * 100);
      });
    }
  );
}

app.post("/api/create-order", (req, res) => {
  const { roll_number, exam_type, exam_month, exam_year, mode, semester } = req.body || {};

  if (!roll_number || !exam_type || !exam_month || !exam_year) {
    return res.status(400).json({ error: "Missing payment fields" });
  }

  computeExamFee(roll_number.trim(), exam_type, mode, semester, (err, feeAmount) => {
    const amount = feeAmount || 0;
    const options = {
      amount: Number(amount),
    currency: "INR",
    receipt: `HT-${roll_number}-${exam_type}-${exam_month}-${exam_year}`,
    };

    razorpay.orders.create(options, (oErr, order) => {
      if (oErr) {
        console.error("Order create error:", oErr);
        return res.status(500).json({ error: "Payment init failed" });
      }

      db.query(
        `INSERT INTO payments
         (roll_number, exam_type, exam_month, exam_year, amount, status, approval_status, razorpay_order_id)
         VALUES (?,?,?,?,?, 'created', 'pending', ?)`,
        [roll_number, exam_type, exam_month, exam_year, options.amount, order.id],
        (qErr) => {
          if (qErr) {
            console.error("DB error inserting payment:", qErr);
            // still return order so front-end can attempt payment; admin can reconcile later
          }
          return res.json({ orderId: order.id, keyId: process.env.RAZORPAY_KEY_ID || "", amount: options.amount });
        }
      );
    });
  });
});

// Verify Razorpay payment signature and mark as paid
app.post("/api/verify-payment", (req, res) => {
  const {
    roll_number,
    exam_type,
    exam_month,
    exam_year,
    razorpay_order_id,
    razorpay_payment_id,
    razorpay_signature,
  } = req.body || {};

  if (!razorpay_order_id || !razorpay_payment_id || !razorpay_signature) {
    return res.status(400).json({ ok: false, error: "Missing payment verification fields" });
  }

  const body = `${razorpay_order_id}|${razorpay_payment_id}`;
  const expected = crypto
    .createHmac("sha256", process.env.RAZORPAY_KEY_SECRET || "")
    .update(body.toString())
    .digest("hex");

  if (expected !== razorpay_signature) {
    return res.status(400).json({ ok: false, error: "Signature mismatch" });
  }

  db.query(
    `UPDATE payments
     SET status='paid', razorpay_payment_id=?, razorpay_signature=?, paid_at=NOW()
     WHERE roll_number=? AND exam_type=? AND exam_month=? AND exam_year=? AND razorpay_order_id=?
     ORDER BY id DESC LIMIT 1`,
    [
      razorpay_payment_id,
      razorpay_signature,
      roll_number,
      exam_type,
      exam_month,
      exam_year,
      razorpay_order_id,
    ],
    (err) => {
      if (err) {
        console.error("DB error updating payment:", err);
        return res.status(500).json({ ok: false, error: "Database error" });
      }
      return res.json({ ok: true });
    }
  );
});

// Mark a Razorpay order as cancelled (user closed payment window)
app.post("/api/payment-cancel", (req, res) => {
  const {
    roll_number,
    exam_type,
    exam_month,
    exam_year,
    razorpay_order_id,
  } = req.body || {};

  if (!roll_number || !razorpay_order_id) {
    return res
      .status(400)
      .json({ ok: false, error: "roll_number and razorpay_order_id required" });
  }

  db.query(
    `UPDATE payments
       SET status='cancelled'
     WHERE roll_number=?
       AND razorpay_order_id=?
       AND status <> 'paid'
     ORDER BY id DESC
     LIMIT 1`,
    [roll_number, razorpay_order_id],
    (err, result) => {
      if (err) {
        console.error("DB error updating cancelled payment:", err);
        return res.status(500).json({ ok: false, error: "Database error" });
      }
      // Even if no row was updated, respond ok to avoid client-side noise
      return res.json({ ok: true });
    }
  );
});

// HOME PAGE
app.get("/", (req, res) => {
  // use your current main UI file
  res.render("index_beach_location"); // change to "index" if needed
});

// DOWNLOAD HALLTICKET PAGE (view-only, shows status and download links for approved sessions)
app.get("/hallticket-download", (req, res) => {
  res.render("hallticket_download");
});

// SIMPLE VERIFICATION PAGE FOR QR SCANS
app.get("/verify-halltkt", (req, res) => {
  const { token } = req.query;
  if (!token) {
    return res
      .status(400)
      .send("Invalid hallticket verification link (missing token).");
  }

  const sql = `
    SELECT v.roll_number, v.exam_type, v.exam_month, v.exam_year,
           v.generated_at, v.verified_at, v.status,
           s.name, s.department, s.semester
    FROM hallticket_verifications v
    LEFT JOIN students s ON s.roll_number = v.roll_number
    WHERE v.token = ?
    LIMIT 1
  `;

  db.query(sql, [token], (err, rows) => {
    if (err) {
      console.error("Verify hallticket DB error:", err);
      return res.status(500).send("Error verifying hallticket. Please try again later.");
    }
    if (!rows || !rows.length) {
      return res.status(404).send("Hallticket verification token not found or invalid.");
    }

    const h = rows[0];

    // Mark first time verification timestamp (optional, ignore errors)
    if (!h.verified_at) {
      db.query(
        "UPDATE hallticket_verifications SET verified_at = NOW() WHERE token = ?",
        [token],
        () => {}
      );
    }

    if (h.status !== "active") {
      return res
        .status(410)
        .send("This hallticket has been revoked or is no longer active.");
    }

    const html = `<!DOCTYPE html>
    <html lang="en"><head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>MITS Hallticket Verification</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
      <div class="container py-5">
        <div class="row justify-content-center">
          <div class="col-md-7">
            <div class="card shadow-sm">
              <div class="card-body">
                <h4 class="mb-2 text-success">Hallticket Verified</h4>
                <p class="text-muted mb-3 small">This hallticket record is valid in the MITS examination system.</p>
                <dl class="row small mb-0">
                  <dt class="col-sm-4">Student</dt><dd class="col-sm-8">${
                    h.name || "(Name not found)"
                  }</dd>
                  <dt class="col-sm-4">Hall Ticket No.</dt><dd class="col-sm-8">${
                    h.roll_number
                  }</dd>
                  <dt class="col-sm-4">Department / Sem</dt><dd class="col-sm-8">${
                    h.department || "-"
                  } / ${h.semester || "-"}</dd>
                  <dt class="col-sm-4">Exam</dt><dd class="col-sm-8">${
                    h.exam_type
                  } – ${h.exam_month} ${h.exam_year}</dd>
                  <dt class="col-sm-4">Issued At</dt><dd class="col-sm-8">${
                    h.generated_at
                  }</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
    </body></html>`;

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(html);
  });
});

// GET STUDENT DETAILS (roll + dob)
app.post("/api/get-student", (req, res) => {
  const { roll_number, dob } = req.body;
  if (!roll_number || !dob) {
    return res.status(400).json({ error: "Roll number & DOB required" });
  }

  const sql = `
    SELECT roll_number, name, father_name,
           DATE_FORMAT(dob, '%Y-%m-%d') AS dob,
           gender, mobile, department, regulation, year,
           semester, section, photo_path, mother_name, caste
    FROM students
    WHERE roll_number = ? AND dob = ?
    LIMIT 1
  `;

  db.query(sql, [roll_number, dob], (err, results) => {
    if (err) {
      console.error("DB error:", err);
      return res.status(500).json({ error: "Database error" });
    }
    if (!results || results.length === 0) {
      return res.status(404).json({ error: "Student not found" });
    }

    const student = results[0];
    let photo_base64 = null;

    try {
      let finalPath = null;

      if (student.photo_path && fs.existsSync(student.photo_path)) {
        finalPath = student.photo_path;
      } else {
        const fallback = path.join(UPLOADS_DIR, `${student.roll_number}.jpg`);
        if (fs.existsSync(fallback)) finalPath = fallback;
      }

      if (finalPath) {
        const buf = fs.readFileSync(finalPath);
        if (isSafeImage(buf)) {
          photo_base64 = `data:image/jpeg;base64,${buf.toString("base64")}`;
        } else {
          console.warn("Stored photo failed image safety check:", finalPath);
        }
      }
    } catch (e) {
      console.error("Photo loading failed:", e);
    }

    res.json({ ...student, photo_base64 });
  });
});

// LIST PAYMENT SESSIONS FOR A STUDENT
app.get("/api/payment-status", (req, res) => {
  const { roll_number } = req.query;
  if (!roll_number) {
    return res.status(400).json({ error: "roll_number is required" });
  }

  const sql = `
    SELECT id AS payment_id, exam_type, exam_month, exam_year, amount, status, approval_status,
           created_at, paid_at
    FROM payments
    WHERE roll_number = ?
    ORDER BY id DESC
    LIMIT 20
  `;

  db.query(sql, [roll_number.trim()], (err, rows) => {
    if (err) {
      console.error("DB error (payment-status):", err);
      return res.status(500).json({ error: "Database error" });
    }
    return res.json(rows || []);
  });
});

// GET SUBJECTS
// - For Regular exams: returns full curriculum subjects for the given dept/reg/semester
// - For Supplementary exams (when exam_type=Supplementary and roll_number is provided):
//   returns only backlog subjects for that student & semester from student_backlogs
app.get("/api/subjects", (req, res) => {
  const { department, regulation, semester, exam_type, roll_number } = req.query;

  const isSupplementary =
    exam_type && exam_type.toLowerCase() === "supplementary" && roll_number;

  if (!department || !regulation || (!semester && !isSupplementary)) {
    return res
      .status(400)
      .json({ error: "department, regulation, semester required" });
  }

  if (isSupplementary) {
    const sqlSupp = `
      SELECT s.id, s.subject_code, s.subject_name, s.semester
      FROM student_backlogs sb
      JOIN subjects s ON sb.subject_id = s.id
      WHERE sb.roll_number = ?
        AND s.department = ?
        AND s.regulation = ?
      ORDER BY s.semester, s.id
    `;

    return db.query(
      sqlSupp,
      [roll_number.trim(), department.trim(), regulation.trim()],
      (err, rows) => {
        if (err) {
          console.error("DB error (supp subjects):", err);
          return res.status(500).json({ error: "Database error" });
        }
        return res.json(rows || []);
      }
    );
  }

  const sql = `
    SELECT id, subject_code, subject_name
    FROM subjects
    WHERE department = ?
      AND regulation = ?
      AND semester = ?
    ORDER BY id
  `;

  db.query(
    sql,
    [department.trim(), regulation.trim(), semester.trim()],
    (err, rows) => {
      if (err) {
        console.error("DB error (subjects):", err);
        return res.status(500).json({ error: "Database error" });
      }
      res.json(rows || []);
    }
  );
});

// GENERATE HALLTICKET
app.post("/generate-halltkt", upload.single("photo"), async (req, res) => {
  try {
    let {
      mode,
      roll_number,
      name,
      father_name,
      mother_name,
      caste,
      dob,
      department,
      year,
      semester,
      section,
      mobile,
      gender,
      exam_type,
      exam_month,
      exam_year,
      regulation,
      device_gps, // comes from hidden field in form if you add it on front-end
      payment_id,
    } = req.body;

    if (!roll_number || !name || !exam_type || !exam_month || !exam_year) {
      return res.status(400).send("Missing required fields");
    }

    // Create or reuse a stable verification token per hallticket session
    let qrDataUrl = null;
    let verifyToken = null;
    try {
      // 1) Try to find an existing token for this student and exam session
      const existingToken = await new Promise((resolve) => {
        db.query(
          `SELECT token FROM hallticket_verifications
           WHERE roll_number=? AND exam_type=? AND exam_month=? AND exam_year=?
             AND status='active'
           ORDER BY id DESC LIMIT 1`,
          [roll_number, exam_type, exam_month, exam_year],
          (err, rows) => {
            if (err) {
              console.error("Error reading hallticket_verifications:", err);
              return resolve(null);
            }
            if (!rows || !rows.length) return resolve(null);
            return resolve(rows[0].token);
          }
        );
      });

      if (existingToken) {
        verifyToken = existingToken;
      } else {
        // 2) Generate a new random token
        verifyToken = crypto.randomBytes(16).toString("hex");
        db.query(
          `INSERT INTO hallticket_verifications
             (token, roll_number, exam_type, exam_month, exam_year)
           VALUES (?,?,?,?,?)`,
          [verifyToken, roll_number, exam_type, exam_month, exam_year],
          (err) => {
            if (err) console.error("Error inserting hallticket_verifications:", err);
          }
        );
      }

      // 3) Build verification URL and generate QR as data URL
      const baseUrl =
        process.env.PUBLIC_BASE_URL || "https://hallticket.vishnulabs.dev";
      const verifyUrl = `${baseUrl}/verify-halltkt?token=${encodeURIComponent(verifyToken)}`;
      qrDataUrl = await QRCode.toDataURL(verifyUrl, { margin: 1, scale: 3 });
    } catch (e) {
      console.error("QR generation error:", e);
      qrDataUrl = null;
    }

    // ---------- PAYMENT + APPROVAL GATE ----------
    try {
      const gate = await new Promise((resolve) => {
        // If a specific payment_id is provided (download page), validate only that row
        if (payment_id) {
          return db.query(
            `SELECT status, approval_status, exam_type AS p_exam_type, exam_month AS p_exam_month, exam_year AS p_exam_year
             FROM payments
             WHERE id = ? AND roll_number = ?
             LIMIT 1`,
            [payment_id, roll_number],
            (perr, rows) => {
              if (perr) {
                console.error("Payment check error (by id):", perr);
                return resolve({ allowed: true });
              }
              if (!rows || !rows.length) {
                return resolve({
                  allowed: false,
                  code: 402,
                  message:
                    "Exam fee not found for this payment. Please contact admin.",
                });
              }
              const pay = rows[0];
              if (pay.status !== "paid") {
                return resolve({
                  allowed: false,
                  code: 402,
                  message:
                    "Payment is not successful yet. Please retry payment or contact admin.",
                });
              }
              if (pay.approval_status !== "approved") {
                return resolve({
                  allowed: false,
                  code: 403,
                  message:
                    "Payment received. Hallticket will be released after admin approval (attendance/fee check).",
                });
              }

              // Override exam session fields from the validated payment row for safety
              exam_type = pay.p_exam_type;
              exam_month = pay.p_exam_month;
              exam_year = pay.p_exam_year;

              return resolve({ allowed: true });
            }
          );
        }

        // Fallback: original behaviour based on latest payment for that exam session
        db.query(
          `SELECT status, approval_status
           FROM payments
           WHERE roll_number=? AND exam_type=? AND exam_month=? AND exam_year=?
           ORDER BY id DESC LIMIT 1`,
          [roll_number, exam_type, exam_month, exam_year],
          (perr, rows) => {
            if (perr) {
              console.error("Payment check error:", perr);
              return resolve({ allowed: true }); // do not hard-block on DB error
            }
            if (!rows || !rows.length) {
              return resolve({
                allowed: false,
                code: 402,
                message:
                  "Exam fee not paid for this exam session. Please complete payment first.",
              });
            }
            const pay = rows[0];
            if (pay.status !== "paid") {
              return resolve({
                allowed: false,
                code: 402,
                message:
                  "Payment is not successful yet. Please retry payment or contact admin.",
              });
            }
            if (pay.approval_status !== "approved") {
              return resolve({
                allowed: false,
                code: 403,
                message:
                  "Payment received. Hallticket will be released after admin approval (attendance/fee check).",
              });
            }
            return resolve({ allowed: true });
          }
        );
      });

      if (!gate.allowed) {
        return res.status(gate.code || 403).send(gate.message || "Hallticket not released yet.");
      }
    } catch (e) {
      console.error("Payment gate error:", e);
    }

    if (!mode) mode = "College";
    if (!regulation) regulation = "R23";

    // SUBJECTS: may be single or array. For download-only (no subjects in body),
    // auto-load subjects from DB based on exam_type (Regular vs Supplementary).
    let subjectsRaw = req.body.subjects || [];
    if (!Array.isArray(subjectsRaw)) subjectsRaw = subjectsRaw ? [subjectsRaw] : [];

    let subjects = [];

    if (subjectsRaw.length > 0) {
      subjects = subjectsRaw.map((v) => {
        const parts = String(v).split("||");
        return { code: (parts[0] || "").trim(), name: (parts[1] || "").trim() };
      });
    } else {
      try {
        const examTypeLower = (exam_type || "").toLowerCase();

        if (examTypeLower === "supplementary") {
          // Load backlog subjects for this student from student_backlogs
          subjects = await new Promise((resolve) => {
            const sql = `
              SELECT s.subject_code, s.subject_name, s.semester
              FROM student_backlogs sb
              JOIN subjects s ON sb.subject_id = s.id
              WHERE sb.roll_number = ?
                AND s.department = ?
                AND s.regulation = ?
              ORDER BY s.semester, s.id
            `;
            db.query(
              sql,
              [roll_number, department, regulation],
              (err, rows) => {
                if (err) {
                  console.error("Error loading backlog subjects for download:", err);
                  return resolve([]);
                }
                resolve(
                  (rows || []).map((r) => ({
                    code: (r.subject_code || "").trim(),
                    name: (r.subject_name || "").trim(),
                  }))
                );
              }
            );
          });
        } else {
          // Regular exam: load curriculum subjects for the student's department/regulation/semester
          subjects = await new Promise((resolve) => {
            const sql = `
              SELECT subject_code, subject_name
              FROM subjects
              WHERE department = ?
                AND regulation = ?
                AND semester = ?
              ORDER BY id
            `;
            db.query(
              sql,
              [department, regulation, semester],
              (err, rows) => {
                if (err) {
                  console.error("Error loading regular subjects for download:", err);
                  return resolve([]);
                }
                resolve(
                  (rows || []).map((r) => ({
                    code: (r.subject_code || "").trim(),
                    name: (r.subject_name || "").trim(),
                  }))
                );
              }
            );
          });
        }
      } catch (e) {
        console.error("Subject auto-load error for download:", e);
        subjects = [];
      }
    }

    // ---- SECURE PHOTO HANDLING ----
    let photoDataUrl = null;
    try {
      const finalPath = path.join(UPLOADS_DIR, `${roll_number}.jpg`);

      if (req.file) {
        const uploadedBuffer = fs.readFileSync(req.file.path);

        // Deep validation using magic bytes
        if (!isSafeImage(uploadedBuffer)) {
          console.warn(
            "Unsafe / non-image upload blocked:",
            req.file.originalname
          );
          fs.unlinkSync(req.file.path);
          return res
            .status(400)
            .send("Invalid photo file. Only real images (JPG/PNG) allowed.");
        }

        // Replace old file if exists
        if (fs.existsSync(finalPath)) {
          try {
            fs.unlinkSync(finalPath);
          } catch (e) {
            console.warn("Could not remove old photo:", e);
          }
        }

        // Move temp to final path named by roll_number
        fs.renameSync(req.file.path, finalPath);

        // Update DB photo_path
        db.query(
          "UPDATE students SET photo_path = ? WHERE roll_number = ?",
          [finalPath, roll_number],
          (err) => {
            if (err) console.error("Error updating photo_path:", err);
          }
        );

        // Set base64
        photoDataUrl = `data:image/jpeg;base64,${uploadedBuffer.toString(
          "base64"
        )}`;
      } else {
        // No upload this time, load existing if present
        if (fs.existsSync(finalPath)) {
          const buf = fs.readFileSync(finalPath);
          if (isSafeImage(buf)) {
            photoDataUrl = `data:image/jpeg;base64,${buf.toString("base64")}`;
          } else {
            console.warn(
              "Existing stored photo failed safety check:",
              finalPath
            );
          }
        }
      }
    } catch (e) {
      console.error("Secure photo handling error:", e);
    }

    // ---------- HALLTICKET DB LOG (as you requested YES) ----------
    try {
      db.query(
        `INSERT INTO halltickets (roll_number, exam_type, exam_month, exam_year)
         VALUES (?, ?, ?, ?)`,
        [roll_number, exam_type, exam_month, exam_year],
        (err) => {
          if (err) console.error("Error inserting hallticket log:", err);
        }
      );
    } catch (e) {
      console.error("Hallticket log error:", e);
    }

    // ------------- CONNECTION LOG -------------
    const hallticketInfo = `Exam: ${exam_type} / ${exam_month} ${exam_year}, Dept: ${department}, Sem: ${semester}, Reg: ${regulation}, Subjects: ${subjects
      .map((s) => s.code)
      .join(", ")}`;

    await logConnection(req, {
      roll_number,
      name,
      semester,
      hallticketInfo,
      device_gps,
    });
    // ------------------------------------------

    // Choose template file based on mode
    const templateFile =
      mode === "University"
        ? "hallticket-template-university.ejs"
        : "hallticket-template-auto.ejs";

    const html = await ejs.renderFile(
      path.join(__dirname, "views", templateFile),
      {
        mode,
        roll_number,
        name,
        father_name,
        mother_name,
        caste,
        dob,
        department,
        year,
        semester,
        section,
        mobile,
        gender,
        exam_type,
        exam_month,
        exam_year,
        regulation,
        subjects,
        photoDataUrl,
        qrDataUrl,
      }
    );

    // Save debug HTML (optional)
    fs.writeFileSync("debug.html", html, "utf8");

    // Generate PDF with Puppeteer
    const browser = await puppeteer.launch({
      headless: "new",
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
      ],
    });

    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "networkidle0" });

    const pdfBuffer = await page.pdf({
      format: "A4",
      printBackground: true,
      margin: { top: "0mm", bottom: "0mm", left: "0mm", right: "0mm" },
    });

    await browser.close();

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", 'inline; filename="hallticket.pdf"');
    res.send(pdfBuffer);
  } catch (err) {
    console.error("PDF generation error:", err);
    res.status(500).send("Error generating hall ticket");
  }
});

// ---------- START SERVER ----------
const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT} and https://hallticket.vishnulabs.dev/`);
});
