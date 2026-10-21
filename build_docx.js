const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  ExternalHyperlink, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, LevelFormat,
} = require('docx');
const fs = require('fs');

const TEAL = '0F766E';
const DARK = '1F2937';
const GREY = '6B7280';
const LINK = '1155CC';
const RULE = 'D1D5DB';

// ---- external authoritative sources (E-E-A-T / GEO) ----------------------
const URL = {
  ibm: 'https://www.ibm.com/reports/data-breach',
  owasp: 'https://owasp.org/www-project-top-ten/',
  hhsRisk: 'https://www.hhs.gov/hipaa/for-professionals/security/guidance/guidance-risk-analysis',
  cfr: 'https://www.ecfr.gov/current/title-45/section-164.308',
  anchor: 'https://bluegoatcyber.com/services/hipaa-penetration-testing',
  // internal
  home: 'https://www.diseasefix.com/',
  about: 'https://www.diseasefix.com/about/',
  conditions: 'https://www.diseasefix.com/diseases-and-conditions/',
  heart: 'https://www.diseasefix.com/heart/pericarditis/',
  cancers: 'https://www.diseasefix.com/cancers/',
  kidney: 'https://www.diseasefix.com/kidney-health/',
  write: 'https://www.diseasefix.com/write-for-us/',
};

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
    spacing: { after: 170, line: 290 },
    ...opts,
  });
}
function crosshead(text) {
  return new Paragraph({
    children: [run(text, { bold: true, color: TEAL, size: 26 })],
    spacing: { before: 300, after: 120 },
    heading: HeadingLevel.HEADING_1,
  });
}
function bullet(children) {
  return new Paragraph({
    children: Array.isArray(children) ? children : [run(children)],
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 90, line: 282 },
  });
}
function hr() {
  return new Paragraph({
    spacing: { before: 140, after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 1 } },
    children: [run('')],
  });
}

// shaded sidebar / callout
function callout(titleText, bodyChildren, fill = 'F0FDFA', barColor = TEAL) {
  const cell = new TableCell({
    width: { size: 9180, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill, color: 'auto' },
    margins: { top: 140, bottom: 140, left: 190, right: 190 },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: fill },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: fill },
      right: { style: BorderStyle.SINGLE, size: 2, color: fill },
      left: { style: BorderStyle.SINGLE, size: 26, color: barColor },
    },
    children: [
      new Paragraph({
        children: [run(titleText, { bold: true, color: barColor, size: 19 })],
        spacing: { after: 90 },
      }),
      ...bodyChildren,
    ],
  });
  return new Table({
    columnWidths: [9180],
    width: { size: 9180, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({ children: [cell] })],
  });
}
// a stat line inside the fact box
function stat(figure, labelText) {
  return new Paragraph({
    spacing: { after: 70, line: 276 },
    children: [
      run(figure + '  ', { bold: true, color: DARK, size: 24 }),
      run(labelText, { color: DARK, size: 19 }),
    ],
  });
}

// ---- content -------------------------------------------------------------
const C = [];

// Headline + dek + byline (journalistic masthead)
C.push(new Paragraph({
  children: [run('To Protect Your Medical Records, Hospitals Are Paying People to Break In', { bold: true, color: DARK, size: 40 })],
  spacing: { after: 110 },
}));
C.push(new Paragraph({
  children: [run('Penetration testing has become a quiet front line in the fight to keep patient data out of criminal hands. Here is how it works, and why regulators increasingly expect it.', { italics: true, color: GREY, size: 23 })],
  spacing: { after: 140 },
}));
C.push(new Paragraph({
  children: [
    run('By the DiseaseFix Health Desk', { bold: true, color: DARK, size: 18 }),
    run('   ·   Reviewed against primary sources   ·   Published October 21, 2026   ·   6 minute read', { color: GREY, size: 18 }),
  ],
  spacing: { after: 150 },
}));
C.push(hr());

// Lede (narrative)
C.push(para([run('Somewhere on a hospital network tonight, someone is trying to steal patient records. In a growing number of cases, the hospital hired them to do it.', { size: 23 })]));

C.push(para('The practice is called penetration testing, and in American healthcare it has moved from a niche technical chore to a front line defense for some of the most sensitive information a person owns. The testers are paid to think like criminals, to find the unlocked digital doors before anyone with bad intentions does, and to hand over a map of every weakness they find.'));

// Nut graf
C.push(para('It is a strange arrangement, and an increasingly common one. Medical records have become one of the most valuable targets online, worth more on criminal markets than stolen card numbers because a diagnosis cannot be canceled and reissued. The cost of getting security wrong, measured in dollars and in exposed lives, has pushed hospitals, device makers, and health technology startups toward a counterintuitive conclusion: the surest way to learn whether your defenses hold is to attack them yourself.'));

// A crime that pays
C.push(crosshead('A crime that pays'));
C.push(para([
  run('For criminals, healthcare is a rich and reliable target. The '),
  link('IBM Cost of a Data Breach Report for 2024', URL.ibm),
  run(' put the average healthcare breach at 9.77 million dollars, the costliest of any industry for the fourteenth year in a row. The next closest sector, financial services, averaged 6.08 million. Across all industries the global average was 4.88 million.'),
]));
C.push(para([
  run('Those figures are abstract until you remember what sits inside the records. The same information readers come to DiseaseFix to understand, whether they are researching '),
  link('heart conditions', URL.heart),
  run(', '),
  link('cancer', URL.cancers),
  run(', or '),
  link('kidney disease', URL.kidney),
  run(', is exactly what a breach spills into the open. Once it is loose, it stays loose.'),
]));

// Fact box (AEO + journalistic sidebar)
C.push(callout('BY THE NUMBERS: HEALTHCARE DATA BREACHES, 2024', [
  stat('9.77M', 'dollars: the average cost of a healthcare data breach'),
  stat('14', 'straight years healthcare has been the costliest industry to breach'),
  stat('6.08M', 'dollars: the next costliest sector, financial services'),
  stat('4.88M', 'dollars: the global average breach across all industries'),
  new Paragraph({
    children: [run('Source: IBM Cost of a Data Breach Report 2024.', { italics: true, color: GREY, size: 17 })],
    spacing: { before: 40, after: 0 },
  }),
]));

// The rule that never says penetration test
C.push(crosshead('The rule that never says "penetration test"'));
C.push(para([
  run('The law at the center of all this is the Health Insurance Portability and Accountability Act, passed in 1996 and known to nearly everyone as HIPAA. Its Security Rule requires any organization handling electronic protected health information, shortened to ePHI, to protect that data’s confidentiality, integrity, and availability. Tucked into the regulation, at '),
  link('45 CFR 164.308(a)(1)(ii)(A)', URL.cfr),
  run(', is a requirement that sounds mundane and turns out to be the whole ballgame: a thorough risk analysis.'),
]));
C.push(para('Here is the catch. HIPAA never uses the words penetration test. It describes the destination, not the route. It tells organizations to understand where patient data could be exposed and leaves the method to them. That gap, between what the law demands and how an organization proves it has delivered, is where the testers make their living.'));

// Breaking in, on purpose
C.push(crosshead('Breaking in, on purpose'));
C.push(para([
  run('A penetration test is a controlled, authorized rehearsal of a real attack. Specialist firms that perform '),
  link('hipaa penetration testing', URL.anchor),
  run(' narrow the work to the systems that create, store, or move patient data, then tie every finding back to the Security Rule so it feeds the risk analysis the law requires. Web applications are measured against the '),
  link('OWASP Top 10', URL.owasp),
  run(', the widely used catalog of the most critical web security flaws maintained by the Open Worldwide Application Security Project. Testers chase down business logic errors and places where records could leak, and, crucially, they come back after the fixes to confirm the holes are truly closed.'),
]));
C.push(para('The work follows a familiar arc: scope the systems that touch ePHI, map the attack surface the way an outsider would, attempt controlled exploitation, separate the real risks from the theoretical ones, and deliver a prioritized report. A test, practitioners are quick to stress, is a snapshot. It captures one moment, in one scope, and the ground keeps shifting as new devices and applications come online.'));

// What the regulators are watching
C.push(crosshead('What the regulators are watching'));
C.push(para('Washington has made its expectations clear, and the message is that filing the right paperwork is not the same as being secure. The Department of Health and Human Services enforces HIPAA through its Office for Civil Rights, and the office has trained its attention on risk analysis in particular. In a recent enforcement push focused on ransomware, it found the same failure again and again, inadequate risk analysis, across settlements that together topped 1.1 million dollars.'));
C.push(para([
  run('The office’s '),
  link('risk analysis guidance', URL.hhsRisk),
  run(', first issued in 2010, is pointed but not prescriptive. No single method guarantees compliance, it says, and it steers organizations toward the resources of the National Institute of Standards and Technology. It sets no fixed schedule either, telling organizations to repeat the work whenever their systems or circumstances change. In practice, that has nudged many toward testing at least once a year, and again after any significant change.'),
]));

// Why none of this reaches the patient
C.push(crosshead('Why none of this reaches the patient'));
C.push(para('For the people whose records are at stake, the entire enterprise is meant to be invisible. A security program that works produces no headlines, no breach notice in the mail, no sleepless night. The silence is the product.'));
C.push(para([
  run('The stakes behind that silence are not abstract. A breach can spill mental health histories, HIV status, and genetic results, the kind of detail that cannot be taken back once it is loose. Readers can browse the full '),
  link('list of diseases and conditions', URL.conditions),
  run(' to see just how personal those records can be. And the responsibility, security professionals have long argued, no longer sits with a lone technician in a back office. It runs through clinicians, administrators, and the outside vendors who touch the data, right down to the single reused password that can unlock thousands of files.'),
]));
C.push(para('Which is why, somewhere on a hospital network tonight, a hired stranger is still probing the locks, hoping to fail in the only way that counts: by finding the open door first.'));

C.push(hr());

// Reader Q&A (AEO/GEO, framed as service journalism)
C.push(crosshead('Questions readers ask'));
const faqs = [
  ['Is a penetration test required by HIPAA?',
   'Not by name. HIPAA requires a documented risk analysis under 45 CFR 164.308(a)(1)(ii)(A), but it does not list penetration testing as a mandatory step. A test is one of the clearest ways to satisfy and strengthen that risk analysis, not a separate legal mandate.'],
  ['How often should a healthcare organization test?',
   'There is no fixed legal frequency. Office for Civil Rights guidance says to repeat the risk analysis whenever systems or circumstances change. Many organizations settle on at least once a year, and again after any major change such as a new application or device.'],
  ['Who is qualified to run the test?',
   'Authorized security professionals, whether an internal team or a specialist outside firm. What matters is explicit authorization, healthcare specific scoping of the systems that hold ePHI, and a report that maps each finding back to the HIPAA Security Rule.'],
];
for (const [q, a] of faqs) {
  C.push(new Paragraph({
    children: [run(q, { bold: true, color: DARK, size: 21 })],
    spacing: { before: 150, after: 50 },
    heading: HeadingLevel.HEADING_2,
  }));
  C.push(para(a));
}

C.push(hr());

// Transparency / sourcing box (E-E-A-T)
C.push(callout('HOW WE SOURCED THIS ARTICLE', [
  new Paragraph({
    children: [run('Every figure and claim here is drawn from primary sources. We do not paraphrase secondhand summaries where an original is available.', { color: DARK, size: 19 })],
    spacing: { after: 90 },
  }),
  bulletLink('Breach costs: ', 'IBM Cost of a Data Breach Report 2024', URL.ibm, '.'),
  bulletLink('Risk analysis requirement: ', '45 CFR 164.308(a)(1)(ii)(A)', URL.cfr, ', U.S. electronic Code of Federal Regulations.'),
  bulletLink('Regulator guidance and enforcement: ', 'HHS Office for Civil Rights risk analysis guidance', URL.hhsRisk, '.'),
  bulletLink('Web testing framework: ', 'OWASP Top 10', URL.owasp, ', Open Worldwide Application Security Project.'),
], 'F8FAFC', GREY),

);

// About + internal links footer (E-E-A-T + internal linking)
C.push(new Paragraph({ children: [run('')], spacing: { after: 60 } }));
C.push(new Paragraph({
  children: [
    run('About DiseaseFix:  ', { bold: true, color: DARK, size: 18 }),
    run('DiseaseFix publishes patient focused health and medical information for readers worldwide.', { color: GREY, size: 18 }),
  ],
  spacing: { after: 50 },
}));
C.push(new Paragraph({
  children: [
    link('About', URL.about),
    run('     ', { size: 18 }),
    link('Diseases and conditions', URL.conditions),
    run('     ', { size: 18 }),
    link('Write for us', URL.write),
  ],
  spacing: { after: 60 },
}));
C.push(new Paragraph({
  children: [run('This article is for general information and does not constitute legal or medical advice.', { italics: true, color: GREY, size: 16 })],
}));

// bullet with leading bold + embedded link (defined after use is fine via hoisting? no — function declaration hoists)
function bulletLink(lead, text, url, tail) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 80, line: 276 },
    children: [run(lead, { bold: true, color: DARK, size: 19 }), link(text, url), run(tail, { color: DARK, size: 19 })],
  });
}

// ---- document ------------------------------------------------------------
const doc = new Document({
  creator: 'DiseaseFix Health Desk',
  title: 'To Protect Your Medical Records, Hospitals Are Paying People to Break In',
  description: 'A reported feature on HIPAA penetration testing and healthcare data security.',
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 460, hanging: 260 } } } }],
    }],
  },
  styles: { default: { document: { run: { font: 'Calibri', size: 21, color: DARK } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1300, right: 1300 } } },
    children: C,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync('HIPAA-Penetration-Testing-DiseaseFix.docx', buf);
  console.log('Wrote HIPAA-Penetration-Testing-DiseaseFix.docx', buf.length, 'bytes');
});
