const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  ExternalHyperlink, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, LevelFormat, PageOrientation,
} = require('docx');
const fs = require('fs');

const TEAL = '0F766E';
const DARK = '1F2937';
const GREY = '6B7280';
const LINK = '1155CC';
const RULE = 'D1D5DB';

// ---- helpers -------------------------------------------------------------
function link(text, url) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text, style: 'Hyperlink', color: LINK, underline: {} })],
  });
}
function run(text, opts = {}) { return new TextRun({ text, ...opts }); }

function para(children, opts = {}) {
  return new Paragraph({
    children: Array.isArray(children) ? children : [run(children)],
    spacing: { after: 160, line: 276 },
    ...opts,
  });
}

function h1(text) {
  return new Paragraph({
    children: [run(text, { bold: true, color: TEAL, size: 30 })],
    spacing: { before: 320, after: 140 },
    heading: HeadingLevel.HEADING_1,
  });
}
function h2(text) {
  return new Paragraph({
    children: [run(text, { bold: true, color: DARK, size: 24 })],
    spacing: { before: 220, after: 100 },
    heading: HeadingLevel.HEADING_2,
  });
}

function bullet(children) {
  return new Paragraph({
    children: Array.isArray(children) ? children : [run(children)],
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 90, line: 276 },
  });
}
function numbered(children) {
  return new Paragraph({
    children: Array.isArray(children) ? children : [run(children)],
    numbering: { reference: 'steps', level: 0 },
    spacing: { after: 100, line: 276 },
  });
}

function hr() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 1 } },
    children: [run('')],
  });
}

// shaded callout box (single cell table)
function callout(titleText, bodyChildren, fill = 'ECFDF5', barColor = TEAL) {
  const cell = new TableCell({
    width: { size: 9360, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill, color: 'auto' },
    margins: { top: 120, bottom: 120, left: 180, right: 180 },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: fill },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: fill },
      right: { style: BorderStyle.SINGLE, size: 2, color: fill },
      left: { style: BorderStyle.SINGLE, size: 24, color: barColor },
    },
    children: [
      new Paragraph({
        children: [run(titleText, { bold: true, color: barColor, size: 20 })],
        spacing: { after: 80 },
      }),
      ...bodyChildren,
    ],
  });
  return new Table({
    columnWidths: [9360],
    width: { size: 9360, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({ children: [cell] })],
  });
}

// data table
function cell(children, { header = false, w = 3120 } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: TEAL, color: 'auto' }
      : { type: ShadingType.CLEAR, fill: 'F9FAFB', color: 'auto' },
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    children: [new Paragraph({
      children: Array.isArray(children) ? children
        : [run(children, { bold: header, color: header ? 'FFFFFF' : DARK, size: 19 })],
      spacing: { after: 0 },
    })],
  });
}

// ---- content -------------------------------------------------------------
const children = [];

// Title block
children.push(new Paragraph({
  children: [run('Why Hospitals Now Hire Hackers to Protect Your Medical Records', { bold: true, color: DARK, size: 40 })],
  spacing: { after: 100 },
}));
children.push(new Paragraph({
  children: [run('Inside the quiet security work that keeps electronic patient records out of criminal hands', { italics: true, color: GREY, size: 22 })],
  spacing: { after: 120 },
}));
children.push(new Paragraph({
  children: [
    run('DiseaseFix Health Desk', { color: GREY, size: 18 }),
    run('   |   Updated October 21, 2026', { color: GREY, size: 18 }),
    run('   |   7 minute read', { color: GREY, size: 18 }),
  ],
  spacing: { after: 160 },
}));
children.push(hr());

// Quick answer (AEO)
children.push(callout('QUICK ANSWER', [
  para([
    run('HIPAA penetration testing is an authorized, simulated cyberattack on the systems that hold electronic patient data. Ethical security testers try to break in the way a criminal would, then report every weakness so a healthcare organization can fix it before a real breach happens. HIPAA does not name the practice by law, but it does require a documented risk analysis, and a penetration test is one of the clearest ways to prove those protections actually work. For scoped healthcare engagements, specialist firms offer '),
    link('hipaa penetration testing', 'https://bluegoatcyber.com/services/hipaa-penetration-testing'),
    run(' that maps each finding back to the HIPAA Security Rule.'),
  ], { spacing: { after: 0, line: 276 } }),
]));

// Key takeaways
children.push(h2('Key takeaways'));
children.push(bullet('Healthcare has been the most expensive industry for data breaches for fourteen years running, averaging 9.77 million dollars per breach in 2024.'));
children.push(bullet('HIPAA never uses the words penetration test, yet it requires a thorough risk analysis under 45 CFR 164.308(a)(1)(ii)(A).'));
children.push(bullet('A penetration test simulates a real attack, then maps each finding to the HIPAA Security Rule so results feed directly into that required risk analysis.'));
children.push(bullet('Federal regulators have fined organizations specifically for inadequate risk analysis, not just for breaches themselves.'));
children.push(bullet('Testing is not a one time task; experts advise repeating it regularly and after any major change to systems or devices.'));

// Intro
children.push(h1('A trail of data follows every patient'));
children.push(para('Every time a patient fills out an intake form, refills a prescription, or logs in to a health portal, a trail of deeply personal information moves across computer systems. That information, known in regulatory language as electronic protected health information, or ePHI, has become one of the most valuable prizes for criminals online. Stolen medical records often sell for more than stolen payment card numbers, in part because a diagnosis or a medical history cannot simply be canceled and reissued the way a bank card can.'));
children.push(para([
  run('The information at stake is exactly the kind DiseaseFix readers research every day, whether they are learning about '),
  link('heart conditions', 'https://www.diseasefix.com/heart/pericarditis/'),
  run(', '),
  link('cancer care', 'https://www.diseasefix.com/cancers/'),
  run(', or '),
  link('kidney and urological disease', 'https://www.diseasefix.com/kidney-health/'),
  run('. When that data leaks, the harm is personal and permanent.'),
]));
children.push(para('Against this backdrop, a growing number of hospitals, medical device makers, and health technology startups are turning to a practice that sounds counterintuitive at first: they pay skilled professionals to break into their own systems.'));

// What is it
children.push(h1('What is HIPAA penetration testing?'));
children.push(para('A penetration test is a controlled, authorized simulation of a real attack. Security specialists probe networks, web applications, and connected medical devices the way a criminal would, documenting every weakness they find before anyone with harmful intent does. A HIPAA focused test narrows that work to the systems that create, store, or transmit patient data, then maps each finding back to the Security Rule so the results feed directly into the risk analysis the law demands.'));
children.push(para('The approach borrows from established industry frameworks. Web application assessments, for example, commonly measure a system against the OWASP Top 10, a widely referenced list of the most critical web application security risks maintained by the Open Worldwide Application Security Project. Testers also examine business logic and look specifically for places where protected health information might leak into the wrong hands.'));

// Why attackers (stats table)
children.push(h1('Why does patient data attract so many attackers?'));
children.push(para('Because it is costly to lose. The figures below come from the IBM Cost of a Data Breach Report 2024, one of the most widely cited annual studies of breach economics.'));

children.push(new Table({
  columnWidths: [4680, 2340, 2340],
  width: { size: 9360, type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    left: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    right: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: RULE },
    insideVertical: { style: BorderStyle.SINGLE, size: 2, color: RULE },
  },
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell('Metric', { header: true, w: 4680 }),
      cell('Figure', { header: true, w: 2340 }),
      cell('Year', { header: true, w: 2340 }),
    ]}),
    new TableRow({ children: [
      cell('Average healthcare data breach cost', { w: 4680 }),
      cell('9.77 million dollars', { w: 2340 }),
      cell('2024', { w: 2340 }),
    ]}),
    new TableRow({ children: [
      cell('Consecutive years healthcare ranked costliest industry', { w: 4680 }),
      cell('14', { w: 2340 }),
      cell('2024', { w: 2340 }),
    ]}),
    new TableRow({ children: [
      cell('Next costliest industry (financial services)', { w: 4680 }),
      cell('6.08 million dollars', { w: 2340 }),
      cell('2024', { w: 2340 }),
    ]}),
    new TableRow({ children: [
      cell('Global average breach cost, all industries', { w: 4680 }),
      cell('4.88 million dollars', { w: 2340 }),
      cell('2024', { w: 2340 }),
    ]}),
  ],
}));
children.push(para([run('Source: IBM Cost of a Data Breach Report 2024.', { italics: true, color: GREY, size: 18 })]));

// What HIPAA requires
children.push(h1('What does HIPAA actually require?'));
children.push(para('The federal law that governs this space is the Health Insurance Portability and Accountability Act, passed in 1996 and known to most people simply as HIPAA. Its Security Rule requires any organization that handles ePHI to protect the confidentiality, integrity, and availability of that data. One of the rule’s required provisions, listed at 45 CFR 164.308(a)(1)(ii)(A), is a thorough risk analysis.'));
children.push(para('Notably, HIPAA never uses the phrase penetration test. The law describes outcomes, not tools. It asks organizations to evaluate their safeguards and understand where patient data could be exposed, then leaves the method of doing so to each organization. That space between what the law requires and how an organization satisfies it is where hands on security testing enters the picture.'));

// How it works (numbered)
children.push(h1('How does a HIPAA penetration test work?'));
children.push(para('Most engagements move through a clear sequence. The exact steps vary by provider, but the shape is consistent.'));
children.push(numbered('Scope the environment. The tester identifies every system that creates, stores, or transmits ePHI, from portals and databases to connected medical devices.'));
children.push(numbered('Gather intelligence. The team maps the attack surface the way an outsider would, looking for exposed services and weak entry points.'));
children.push(numbered('Attempt controlled exploitation. Testers safely try to exploit the weaknesses they find, confirming which are real rather than theoretical.'));
children.push(numbered('Map findings to HIPAA. Each confirmed issue is tied back to the Security Rule so it feeds the organization’s required risk analysis.'));
children.push(numbered('Report and review. The organization receives a prioritized report, usually followed by a review session and a plan to fix the highest risks first.'));
children.push(numbered('Retest. After fixes are applied, a focused retest confirms the holes are actually closed.'));

// Regulators
children.push(h1('What do regulators expect?'));
children.push(para('Regulators have made clear that the paperwork of compliance is not enough on its own. The Department of Health and Human Services, through its Office for Civil Rights, enforces HIPAA and has sharpened its focus on risk analysis in particular. In a recent enforcement initiative centered on ransomware cases, the office identified inadequate risk analysis as the common failure across multiple settlements, which together totaled more than 1.1 million dollars in payments.'));
children.push(para('Office for Civil Rights guidance, first issued in 2010, stresses that no single method guarantees compliance and points organizations toward resources from the National Institute of Standards and Technology. It also declines to set a fixed testing schedule, advising instead that organizations repeat their analysis whenever their systems or circumstances change.'));

// Patients
children.push(h1('Why this matters for patients'));
children.push(para('For patients, this activity is invisible, and that is largely the point. A security program that works well produces no headlines at all. But the stakes are real. A breach can expose mental health histories, HIV status, genetic information, and other details that cannot be undone once they are public.'));
children.push(para([
  run('The broader lesson, security professionals say, is cultural. Protecting patient data is no longer solely the job of an IT department tucked away in a back office. It now touches clinicians, administrators, and the third party companies that handle data on a hospital’s behalf. Readers who want to understand the conditions behind those records can explore the full '),
  link('list of diseases and conditions', 'https://www.diseasefix.com/diseases-and-conditions/'),
  run(' on DiseaseFix. In an era when a single weak password can compromise thousands of records, hiring someone trustworthy to find that weakness first has quietly become one of the more important forms of patient care.'),
]));

// FAQ (AEO/GEO)
children.push(h1('Frequently asked questions'));

const faqs = [
  ['Is HIPAA penetration testing legally required?',
   'Not by name. HIPAA requires a documented risk analysis under 45 CFR 164.308(a)(1)(ii)(A), but it does not list penetration testing as a mandatory step. A penetration test is a widely used way to satisfy and strengthen that risk analysis, not a separate legal mandate.'],
  ['What is the difference between a risk analysis and a penetration test?',
   'A risk analysis is the broad, required assessment of where ePHI could be exposed across an organization. A penetration test is a hands on technical exercise that actively probes systems for weaknesses. The test produces evidence that feeds the larger risk analysis.'],
  ['How often should a healthcare organization run a penetration test?',
   'There is no fixed legal frequency. Office for Civil Rights guidance advises repeating a risk analysis whenever systems or circumstances change. In practice, many organizations test at least once a year and again after any major change, such as a new application or device.'],
  ['Who should perform a HIPAA penetration test?',
   'Qualified, authorized security professionals, whether an internal team or a specialist external firm. The key requirements are explicit authorization, healthcare specific scoping of ePHI systems, and a report that maps findings back to the HIPAA Security Rule.'],
  ['Does a clean penetration test mean an organization is fully compliant?',
   'No. A test captures a single moment in time and covers the systems in its scope. Compliance is ongoing, which is why guidance stresses repeating the work after changes rather than treating one clean result as permanent proof.'],
];
for (const [q, a] of faqs) {
  children.push(new Paragraph({
    children: [run(q, { bold: true, color: DARK, size: 21 })],
    spacing: { before: 140, after: 50 },
    heading: HeadingLevel.HEADING_3,
  }));
  children.push(para(a));
}

children.push(hr());

// Sources
children.push(h2('Sources and verified claims'));
children.push(bullet('Average healthcare data breach cost of 9.77 million dollars, costliest industry for the fourteenth consecutive year, financial services at 6.08 million dollars, global average of 4.88 million dollars: IBM Cost of a Data Breach Report 2024.'));
children.push(bullet('HIPAA Security Rule risk analysis requirement at 45 CFR 164.308(a)(1)(ii)(A), covering confidentiality, integrity, and availability of ePHI: U.S. Department of Health and Human Services.'));
children.push(bullet('Office for Civil Rights risk analysis guidance first issued in 2010, no prescribed testing frequency, references to NIST resources: HHS Office for Civil Rights guidance on risk analysis.'));
children.push(bullet('Office for Civil Rights Risk Analysis Initiative identifying inadequate risk analysis across ransomware settlements totaling more than 1.1 million dollars: HHS enforcement actions.'));
children.push(bullet('OWASP Top 10 maintained by the Open Worldwide Application Security Project: OWASP.'));
children.push(bullet('HIPAA enacted in 1996: Health Insurance Portability and Accountability Act of 1996.'));

// Editorial note with internal links
children.push(hr());
children.push(new Paragraph({
  children: [
    run('About DiseaseFix: ', { bold: true, color: DARK, size: 18 }),
    run('DiseaseFix publishes patient focused health and medical information. Learn more on our ', { color: GREY, size: 18 }),
  ],
  spacing: { after: 40 },
}));
children.push(new Paragraph({
  children: [
    link('About page', 'https://www.diseasefix.com/about/'),
    run('  |  ', { color: GREY, size: 18 }),
    link('Diseases and conditions', 'https://www.diseasefix.com/diseases-and-conditions/'),
    run('  |  ', { color: GREY, size: 18 }),
    link('Write for us', 'https://www.diseasefix.com/write-for-us/'),
  ],
  spacing: { after: 40 },
}));
children.push(new Paragraph({
  children: [run('This article is for general information and does not constitute legal or medical advice.', { italics: true, color: GREY, size: 16 })],
}));

// ---- document ------------------------------------------------------------
const doc = new Document({
  creator: 'DiseaseFix Health Desk',
  title: 'Why Hospitals Now Hire Hackers to Protect Your Medical Records',
  description: 'A journalistic explainer on HIPAA penetration testing and healthcare data security.',
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 460, hanging: 260 } } } }],
      },
      {
        reference: 'steps',
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 460, hanging: 260 } } } }],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 21, color: DARK } },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, bottom: 1080, left: 1260, right: 1260 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync('HIPAA-Penetration-Testing-DiseaseFix.docx', buf);
  console.log('Wrote HIPAA-Penetration-Testing-DiseaseFix.docx', buf.length, 'bytes');
});
