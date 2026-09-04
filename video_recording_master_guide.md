# PISI — 5-Minute Video Recording Master Guide & Script
**Track 3: AI Revenue Recovery • Razorpay AI Buildathon 2026**

---

## 🎬 1. Recording Setup & Windows to Prepare Before Hitting Record

Have these **3 tabs / windows** open on your screen:

| Window / Tab | URL or Command | Purpose |
|:---|:---|:---|
| **Tab 1: Slide Deck** | [file:///c:/Users/harih/OneDrive/Documents/PISI/PISI_pitch_deck.html](file:///c:/Users/harih/OneDrive/Documents/PISI/PISI_pitch_deck.html) | Modern full-screen HTML slide deck (press **F** for full screen, use **Right/Left arrows**) |
| **Tab 2: Live Console** | [https://pisi-eosin.vercel.app](https://pisi-eosin.vercel.app) | Production Vercel dashboard with live Render ML engine & Simulate Downtime buttons |
| **Tab 3: Terminal** | `c:\Users\harih\OneDrive\Documents\PISI` | Ready to run `py scripts/batch_eval.py` |

---

## ⏱️ 2. Minute-by-Minute Timeline & Camera Focus Areas

```
┌───────────────┬───────────────────────────────┬──────────────────────────────────────────┐
│ Time          │ What Screen to Show           │ Specific Area to Zoom / Point At         │
├───────────────┼───────────────────────────────┼──────────────────────────────────────────┤
│ 0:00 – 0:35   │ Tab 1: Slides 1 & 2           │ "Two Different Failures" comparison card │
│ 0:35 – 1:15   │ Tab 1: Slides 3, 4 & 5        │ The Gap ASCII diagram & Leg A vs Leg B   │
│ 1:15 – 2:45   │ Tab 2: Live Vercel Dashboard  │ Click "Simulate Downtime" + Ledger + Hash│
│ 2:45 – 3:45   │ Tab 3: Terminal               │ Run batch_eval.py + Exception list       │
│ 3:45 – 4:30   │ Tab 1: Slides 11, 12 & 13     │ Financial impact + Production features   │
│ 4:30 – 5:00   │ Tab 1: Slides 14 & 15         │ Closing punchline + Live URLs            │
└───────────────┴───────────────────────────────┴──────────────────────────────────────────┘
```

---

## 🎙️ 3. Complete Word-for-Word Script & Actions

---

### Segment 1: The Hook & The Dual-Failure Problem (0:00 – 0:35)
* **Screen to Show:** **Slide 1**, then advance to **Slide 2** (`PISI_pitch_deck.html`).
* **Specific Area to Focus:** The two cards on Slide 2 — *Authorization Failure* vs. *Settlement Risk*.
* **Voiceover:**
> *"Hi everyone, this is PISI — Predictive Instant Settlement Intelligence, built for Track 3: AI Revenue Recovery.*
>
> *In digital payments, two completely different things fail during a bank outage. First, a payment can fail at checkout when the customer's card or UPI is debited. Razorpay already solves that before authorization using Smart Routing.*
>
> *But second, what if the payment already succeeded and was captured, but the partner settlement bank goes down right before payout? That's not a customer error — that's a merchant cash-flow crisis. Today, nothing in Razorpay's stack predicts settlement risk ahead of time."*

---

### Segment 2: Razorpay's Stack & The Operational Gap (0:35 – 1:15)
* **Screen to Show:** Advance to **Slide 3**, then **Slide 4**, then **Slide 5**.
* **Specific Area to Focus:** The center ASCII diagram on Slide 4, then Leg A ("Moves Money") on Slide 5.
* **Voiceover:**
> *"Razorpay already has the two core building blocks. Smart Routing achieves 94.69% precision on gateway routing, and Instant Settlement advances payouts at a 0.30% fee.*
>
> *The gap is that Instant Settlement today is 100% reactive. A merchant has to notice the delay themselves and manually click a button, meaning only 15% of at-risk volume is ever protected.*
>
> *PISI bridges this gap with two independent legs: Leg A autonomously pre-approves Instant Settlement advances at a reduced 0.10% predictive fee under a 30% portfolio capital cap. Leg B provides early-warning alerts to merchants without deploying a single rupee of capital."*

---

### Segment 3: The Live Working System Demo (1:15 – 2:45) ⭐ **MONEY MOMENT**
* **Screen to Show:** Switch to **Tab 2: [https://pisi-eosin.vercel.app](https://pisi-eosin.vercel.app)**.
* **Actions & Focus Areas:**
  1. **Zoom in on the Red Simulation Panel at top:**
     - **Action:** Click the red button: **`🔴 SBI — HIGH Downtime`**.
     - **Voiceover:**
       > *"Let's see it live on production. This dashboard on Vercel is connected directly to our FastAPI backend deployed on Render.*
       >
       > *I'll click 'Simulate SBI High Downtime'. Instantly, the backend injects real telemetry into our 5D Bank Vitality Engine."*
  2. **Pan camera down to the Health Spline Graph & Decision Chips:**
     - **Point at:** Health dropping to ~34 HP and Decision turning **`ACTIVATE`** in red/green.
     - **Voiceover:**
       > *"Watch the score: SBI vitality plummets to 34 HP along our smooth spline curve. The decision engine evaluates our 47-feature calibrated XGBoost model, recognizes the severe degradation with high confidence, and triggers Leg A: ACTIVATE."*
  3. **Pan down to the Bridge Key ID & SHA-256 Audit Record:**
     - **Point at:** The unique `BRIDGE-SBI-...` ID and the 64-character cyan SHA-256 hash box.
     - **Voiceover:**
       > *"Notice the compliance grade: PISI generates an immutable 64-character SHA-256 BridgeKeyID receipt. This is verified byte-for-byte against double-entry accounting rules where debits equal credits."*
  4. **Pan up to the Protection Ledger:**
     - **Point at:** **Transactions Protected** (+1), **Protected Volume**, and **Fee Revenue (0.10%)**.
     - **Voiceover:**
       > *"And our Protection Ledger updates in real time, tracking volume deployed against our strict 30% portfolio capital limit."*

---

### Segment 4: Empirical Validation & The Exception List (2:45 – 3:45)
* **Screen to Show:** Switch to **Tab 3: Terminal**.
* **Action:** Run the batch evaluation command:
  ```bash
  py scripts/batch_eval.py
  ```
* **Specific Area to Focus:** The printed confusion matrix and the `DOCUMENTED EXCEPTION LIST`.
* **Voiceover:**
> *"Now let's verify reliability. I'll run our evaluation suite over 100 simulated outage incidents.*
>
> *Look at the terminal output: 100% Precision and 87.5% Recall with an F1 score of 0.9333. Out of 16 genuine risk events, PISI protected 14 with Zero False Positives — meaning zero corporate capital was wasted on false alarms.*
>
> *Over ₹18.77 Lakhs of volume was protected, generating ₹1,877 in revenue and ₹642 in net fee profit after 2-day capital float costs.*
>
> *Most importantly, look at the Documented Exception List: incidents INC-039 and INC-069 were missed because confidence fell slightly below our 0.70 activation floor. We document our misses transparently rather than cherry-picking numbers."*

---

### Segment 5: ML Rigor, Architecture & Production Stack (3:45 – 4:30)
* **Screen to Show:** Switch back to **Tab 1: Slide Deck** (Advance to **Slide 9**, then **Slide 12**, then **Slide 13**).
* **Specific Area to Focus:** Slide 12 (Production-Ready) and Slide 13 (Beyond Scope).
* **Voiceover:**
> *"On adversarial noisy datasets, our trained XGBoost model achieves an F1 of 0.450, beating naive rules across both precision and recall. On the primary benchmark, it achieves an F1 of 0.6965.*
>
> *We built a full production system: live webhook receiver handling 6 Razorpay event types with sub-5ms HMAC-SHA256 signature verification, an Isolation Forest to catch zero-day bank failures, and an automated learning loop that retrains on drift — improving F1 from 0.413 to 0.454 across 5 random seeds."*

---

### Segment 6: Closing & Links (4:30 – 5:00)
* **Screen to Show:** Advance to **Slide 14**, then **Slide 15**.
* **Specific Area to Focus:** The large text on Slide 14, then the live links on Slide 15.
* **Voiceover:**
> *"To wrap up:*
>
> *Smart Routing optimizes the path before authorization. PISI optimizes the safety net after capture.*
>
> *Everything you saw is live today: the dashboard is on Vercel at pisi-eosin.vercel.app, the API is on Render, and the entire repository is open source on GitHub.*
>
> *The fundamental question we leave Razorpay with is: What if the merchant never had to ask?*
>
> *Thank you."*

---

## 🎯 Quick Rehearsal Checklist
- [ ] Open `PISI_pitch_deck.html` in Chrome/Edge, press **F** for Fullscreen.
- [ ] Open `https://pisi-eosin.vercel.app` in a second tab.
- [ ] Open terminal in project folder, pre-typed: `py scripts/batch_eval.py`.
- [ ] Test mic volume and start recording. You are ready to win! 🏆
