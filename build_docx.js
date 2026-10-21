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

const URL = {
  ibm: 'https://www.ibm.com/reports/data-breach',
  owasp: 'https://owasp.org/www-project-top-ten/',
  hhsRisk: 'https://www.hhs.gov/hipaa/for-professionals/security/guidance/guidance-risk-analysis',
  hhsEnforce: 'https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/agreements/index.html',
  cfr: 'https://www.ecfr.gov/current/title-45/section-164.308',
  anchor: 'https://bluegoatcyber.com/services/hipaa-penetration-testing',
  home: 'https://www.diseasefix.com/',
  about: 'https://www.diseasefix.com/about/',
  conditions: 'https://www.diseasefix.com/diseases-and-conditions/',
  heart: 'https://www.diseasefix.com/heart/pericarditis/',
  cancers: 'https://www.diseasefix.com/cancers/',
  kidney: 'https://www.diseasefix.com/kidney-health/',
  write: 'https://www.diseasefix.com/write-for-us/',
};

function link(text, url) {
  return new ExternalHyperlink({ link: url, children: [new TextRun({ text, style: 'Hyperlink', color: LINK, underline: {} })] });
}
function run(text, opts = {}) { return new TextRun({ text, ...opts }); }
function para(children, opts = {}) {
  return new Paragraph({ children: Array.isArray(children) ? children : [run(children)], spacing: { after: 170, line: 290 }, ...opts });
}
function crosshead(text) {
  return new Paragraph({ children: [run(text, { bold: true, color: TEAL, size: 26 })], spacing: { before: 300, after: 120 }, heading: HeadingLevel.HEADING_2 });
}
function bullet(children) {
  return new Paragraph({ children: Array.isArray(children) ? children : [run(children)], numbering: { reference: 'bullets', level: 0 }, spacing: { after: 90, line: 282 } });
}
function bulletLink(lead, text, url, tail) {
  return new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 80, line: 276 },
    children: [run(lead, { bold: true, color: DARK, size: 19 }), link(text, url), run(tail, { color: DARK, size: 19 })] });
}
function hr() {
  return new Paragraph({ spacing: { before: 140, after: 140 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 1 } }, children: [run('')] });
}
function callout(titleText, bodyChildren, fill = 'F0FDFA', barColor = TEAL) {
  const cell = new TableCell({
    width: { size: 9100, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill, color: 'auto' },
    margins: { top: 140, bottom: 140, left: 190, right: 190 },
    borders: { top: { style: BorderStyle.SINGLE, size: 2, color: fill }, bottom: { style: BorderStyle.SINGLE, size: 2, color: fill }, right: { style: BorderStyle.SINGLE, size: 2, color: fill }, left: { style: BorderStyle.SINGLE, size: 26, color: barColor } },
    children: [new Paragraph({ children: [run(titleText, { bold: true, color: barColor, size: 19 })], spacing: { after: 90 } }), ...bodyChildren],
  });
  return new Table({ columnWidths: [9100], width: { size: 9100, type: WidthType.DXA },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [new TableRow({ children: [cell] })] });
}
function stat(figure, labelText) {
  return new Paragraph({ spacing: { after: 70, line: 276 }, children: [run(figure + '  ', { bold: true, color: DARK, size: 24 }), run(labelText, { color: DARK, size: 19 })] });
}

const C = [];

// Title = semantic H1
C.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 110 },
  children: [run('To Protect Your Medical Records, Hospitals Are Paying People to Break In', { bold: true, color: DARK, size: 40 })] }));
C.push(new Paragraph({ children: [run('HIPAA penetration testing has become a quiet front line in the fight to keep patient data out of criminal hands. Here is how it works, and why regulators increasingly expect it.', { italics: true, color: GREY, size: 23 })], spacing: { after: 140 } }));
C.push(new Paragraph({ children: [
  run('By the DiseaseFix Health Desk', { bold: true, color: DARK, size: 18 }),
  run('   ·   Reviewed against primary sources   ·   Published October 21, 2026   ·   5 minute read', { color: GREY, size: 18 }),
], spacing: { after: 150 } }));
C.push(hr());

// Lede
C.push(para([run('Somewhere on a hospital network tonight, someone is trying to steal patient records. In a growing number of cases, the hospital hired them to do it.', { size: 23 })]));
C.push(para('The practice is called penetration testing. In plain terms, it is an authorized, simulated cyberattack on the systems that hold patient data: skilled specialists try to break in the way a criminal would, then hand over a map of every weakness they find so it can be fixed before anyone else does. In American healthcare it has moved from a niche technical chore to a central defense for some of the most sensitive information a person owns.'));
C.push(para('It is a strange arrangement, and an increasingly common one. Medical records are prized by criminals precisely because they cannot be reset. A stolen bank card can be canceled in minutes; a diagnosis, a prescription history, or a genetic result cannot be canceled and reissued. The cost of getting security wrong, measured in dollars and in exposed lives, has pushed hospitals, device makers, and health technology startups toward a counterintuitive conclusion: the surest way to learn whether your defenses hold is to attack them yourself.'));

// A crime that pays
C.push(crosshead('A crime that pays'));
C.push(para([
  run('For criminals, healthcare is a rich and reliable target. The '),
  link('IBM Cost of a Data Breach Report 2026', URL.ibm),
  run(' put the average healthcare breach at 6.64 million dollars. That is down about 10 percent from the year before, and healthcare was the only sector whose costs fell, yet it remains the most expensive industry to breach, a distinction it has held for well over a decade. The report, which studied 602 organizations hit between March 2025 and February 2026, found the global average across all industries at 4.99 million.'),
]));
C.push(para([
  run('Two cautions keep those numbers honest. They are global averages, and in the United States, where this story unfolds, breach costs run far higher and rose again this year. The healthcare figure also rests on a small slice of the organizations studied. Still, the direction is unmistakable, and the stakes stay abstract only until you remember what sits inside the records. The same information readers come to DiseaseFix to understand, whether they are researching a heart condition like '),
  link('pericarditis', URL.heart),
  run(', '),
  link('cancer', URL.cancers),
  run(', or '),
  link('kidney disease', URL.kidney),
  run(', is exactly what a breach spills into the open. Healthcare is also routinely the slowest sector to detect and contain an intrusion, often taking the better part of a year. Once that data is loose, it stays loose.'),
]));

C.push(callout('BY THE NUMBERS: HEALTHCARE DATA BREACHES, 2026', [
  stat('6.64M', 'dollars: the average cost of a healthcare data breach, the highest of any industry'),
  stat('7.42M', 'dollars: last year’s healthcare average; costs fell about 10 percent, the only sector to drop'),
  stat('4.99M', 'dollars: the global average breach across all industries'),
  stat('602', 'organizations studied, breached between March 2025 and February 2026'),
  new Paragraph({ children: [run('Source: IBM Cost of a Data Breach Report 2026.', { italics: true, color: GREY, size: 17 })], spacing: { before: 40, after: 0 } }),
]));

// The rule
C.push(crosshead('The rule that never says "penetration test"'));
C.push(para([
  run('The law at the center of all this is the Health Insurance Portability and Accountability Act, passed in 1996 and known to nearly everyone as HIPAA. Its Security Rule requires any organization handling electronic protected health information, shortened to ePHI, to protect that data’s confidentiality, integrity, and availability. Tucked into the regulation, at '),
  link('45 CFR 164.308(a)(1)(ii)(A)', URL.cfr),
  run(', is a requirement that sounds mundane and turns out to be the crux of the matter: a thorough risk analysis, meaning a documented study of where patient data could be exposed and how badly.'),
]));
C.push(para('Here is the catch. HIPAA never uses the words penetration test. It describes the destination, not the route. It tells organizations to understand where patient data could be exposed and leaves the method to them. That gap, between what the law demands and how an organization proves it has delivered, is where the testers make their living.'));

// Breaking in
C.push(crosshead('Breaking in, on purpose'));
C.push(para([
  run('A penetration test is a controlled, authorized rehearsal of a real attack. That is the premise behind '),
  link('hipaa penetration testing', URL.anchor),
  run(', work that narrows the search to the systems that create, store, or move patient data and ties every finding back to the Security Rule so it feeds the risk analysis the law requires. Web applications are measured against the '),
  link('OWASP Top 10', URL.owasp),
  run(', the widely used catalog of the most critical web security flaws maintained by the Open Worldwide Application Security Project. Testers chase down business logic errors and places where records could leak, and, crucially, they return after the fixes to confirm the holes are truly closed.'),
]));
C.push(para('The work follows a familiar arc: scope the systems that touch ePHI, map the attack surface the way an outsider would, attempt controlled exploitation, separate the real risks from the theoretical ones, and deliver a prioritized report. A test, practitioners are quick to stress, is a snapshot. It captures one moment, in one scope, and the ground keeps shifting as new devices and applications come online.'));

// Regulators
C.push(crosshead('What the regulators are watching'));
C.push(para('Washington has made its expectations clear, and the message is that filing the right paperwork is not the same as being secure. The Department of Health and Human Services enforces HIPAA through its Office for Civil Rights, which in 2024 opened a Risk Analysis Initiative aimed squarely at that one requirement. The pattern it keeps finding, across case after case, is the same: organizations that never performed a risk analysis, did not repeat it often enough, or left it incomplete.'));
C.push(para('The initiative’s first financial penalty put the stakes in plain view. After a 2021 ransomware attack encrypted files holding the records of 14,273 patients, the Bryan County Ambulance Authority in Oklahoma paid 90,000 dollars and agreed to a corrective action plan, with regulators citing a failure to conduct an accurate and thorough risk analysis. More settlements along the same lines have followed.'));
C.push(para([
  run('The office’s '),
  link('risk analysis guidance', URL.hhsRisk),
  run(', first issued in 2010, is pointed but not prescriptive. No single method guarantees compliance, it says, and it steers organizations toward the resources of the National Institute of Standards and Technology. It sets no fixed schedule either, telling organizations to repeat the work whenever their systems or circumstances change. In practice, that has nudged many toward testing at least once a year, and again after any significant change.'),
]));

// Patients
C.push(crosshead('Why none of this reaches the patient'));
C.push(para('For the people whose records are at stake, the entire enterprise is meant to be invisible. A security program that works produces no headlines, no breach notice in the mail, no sleepless night. The silence is the product.'));
C.push(para([
  run('The stakes behind that silence are not abstract. A breach can spill mental health histories, HIV status, and genetic results, the kind of detail that cannot be taken back once it is loose. Readers can browse the full '),
  link('list of diseases and conditions', URL.conditions),
  run(' to see just how personal those records can be. And the responsibility, security professionals have long argued, no longer sits with a lone technician in a back office. It runs through clinicians, administrators, and the outside vendors who touch the data, right down to the single reused password that can unlock thousands of files.'),
]));
C.push(para('Which is why, somewhere on a hospital network tonight, a hired stranger is still probing the locks, hoping to fail in the only way that counts: by finding the open door first.'));

C.push(hr());

// FAQ (section head H2, questions H3)
C.push(crosshead('Questions readers ask'));
const faqs = [
  ['What is HIPAA penetration testing?',
   'HIPAA penetration testing is an authorized, simulated cyberattack on the systems that store or transmit electronic protected health information. Ethical testers try to breach those systems the way a criminal would, then report every weakness so it can be fixed and documented in the risk analysis the HIPAA Security Rule requires.'],
  ['Does HIPAA require penetration testing?',
   'Not by name. HIPAA requires a documented risk analysis under 45 CFR 164.308(a)(1)(ii)(A), but it does not list penetration testing as a mandatory step. A test is one of the clearest ways to satisfy and strengthen that risk analysis, not a separate legal mandate.'],
  ['How often should a healthcare organization run a penetration test?',
   'There is no fixed legal frequency. Office for Civil Rights guidance says to repeat the risk analysis whenever systems or circumstances change. Many organizations settle on at least once a year, and again after any major change such as a new application or device.'],
  ['How much does HIPAA penetration testing cost?',
   'There is no standard price. The cost depends on how many systems, applications, and devices fall in scope, and whether the work covers networks, web applications, or connected medical devices. A single application test and a full health system assessment are very different jobs, so reputable providers price only after scoping the environment.'],
  ['What is the difference between a penetration test and a vulnerability scan?',
   'A vulnerability scan is automated. It checks systems against a database of known weaknesses and produces a list. A penetration test goes further: a human tester tries to exploit those weaknesses to confirm which are genuinely dangerous and how far a real attacker could get.'],
  ['Who is qualified to run the test?',
   'Authorized security professionals, whether an internal team or a specialist outside firm. What matters is explicit authorization, healthcare specific scoping of the systems that hold ePHI, and a report that maps each finding back to the HIPAA Security Rule.'],
];
for (const [q, a] of faqs) {
  C.push(new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 150, after: 50 },
    children: [run(q, { bold: true, color: DARK, size: 21 })] }));
  C.push(para(a));
}

C.push(hr());

// Sourcing box
C.push(callout('HOW WE SOURCED THIS ARTICLE', [
  new Paragraph({ children: [run('Every figure and claim here is drawn from primary sources and reflects the most recent data available at publication. Industry breach costs rest on a subset of the organizations studied and are global averages; United States costs run higher. We do not paraphrase secondhand summaries where an original exists.', { color: DARK, size: 19 })], spacing: { after: 90 } }),
  bulletLink('Breach costs and response times: ', 'IBM Cost of a Data Breach Report 2026', URL.ibm, '.'),
  bulletLink('Risk analysis requirement: ', '45 CFR 164.308(a)(1)(ii)(A)', URL.cfr, ', U.S. electronic Code of Federal Regulations.'),
  bulletLink('Regulator guidance: ', 'HHS Office for Civil Rights risk analysis guidance', URL.hhsRisk, ' (first issued 2010).'),
  bulletLink('Enforcement actions: ', 'HHS OCR resolution agreements and civil money penalties', URL.hhsEnforce, ', including the Bryan County Ambulance Authority settlement.'),
  bulletLink('Web testing framework: ', 'OWASP Top 10', URL.owasp, ', Open Worldwide Application Security Project.'),
], 'F8FAFC', GREY));

// About the author / editorial process (generic staff bio for E-E-A-T)
C.push(new Paragraph({ children: [run('')], spacing: { after: 40 } }));
C.push(callout('ABOUT THE DISEASEFIX HEALTH DESK', [
  new Paragraph({ spacing: { after: 0, line: 282 }, children: [run('This article was researched and written by the DiseaseFix Health Desk, the publication’s in house editorial team covering health, medicine, and the systems that protect patient data. Every piece is checked against primary and authoritative sources, government regulations, official guidance, and named industry reports, before it is published, and figures are updated as newer data is released. DiseaseFix publishes patient focused health information for readers worldwide.', { color: DARK, size: 19 })] }),
], 'F8FAFC', TEAL));
C.push(new Paragraph({ children: [run('')], spacing: { after: 40 } }));
C.push(new Paragraph({ children: [link('About', URL.about), run('     ', { size: 18 }), link('Diseases and conditions', URL.conditions), run('     ', { size: 18 }), link('Write for us', URL.write)], spacing: { after: 60 } }));
C.push(new Paragraph({ children: [run('This article is for general information and does not constitute legal or medical advice.', { italics: true, color: GREY, size: 16 })], spacing: { after: 60 } }));

C.push(hr());

// Editor publishing notes
C.push(callout('EDITOR’S PUBLISHING NOTES (SEO / AEO)', [
  new Paragraph({ spacing: { after: 70, line: 276 }, children: [run('Meta title:  ', { bold: true, color: DARK, size: 18 }), run('HIPAA Penetration Testing: Why Hospitals Hire Ethical Hackers', { color: DARK, size: 18 })] }),
  new Paragraph({ spacing: { after: 70, line: 276 }, children: [run('Meta description:  ', { bold: true, color: DARK, size: 18 }), run('What HIPAA penetration testing is, what the HIPAA Security Rule actually requires, and why healthcare breaches averaged 6.64 million dollars in 2026.', { color: DARK, size: 18 })] }),
  new Paragraph({ spacing: { after: 70, line: 276 }, children: [run('Suggested slug:  ', { bold: true, color: DARK, size: 18 }), run('hipaa-penetration-testing-healthcare-data', { color: DARK, size: 18 })] }),
  new Paragraph({ spacing: { after: 70, line: 276 }, children: [run('Primary keyword:  ', { bold: true, color: DARK, size: 18 }), run('hipaa penetration testing', { color: DARK, size: 18 })] }),
  new Paragraph({ spacing: { after: 0, line: 276 }, children: [run('Structured data:  ', { bold: true, color: DARK, size: 18 }), run('Ship the companion file HIPAA-Penetration-Testing-DiseaseFix.schema.html (Article + FAQPage JSON-LD) in the page head.', { color: DARK, size: 18 })] }),
], 'FFFBEB', 'B45309'));

const doc = new Document({
  creator: 'DiseaseFix Health Desk',
  title: 'To Protect Your Medical Records, Hospitals Are Paying People to Break In',
  description: 'A reported feature on HIPAA penetration testing and healthcare data security.',
  numbering: { config: [{ reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } }] }] },
  styles: { default: { document: { run: { font: 'Calibri', size: 21, color: DARK } } } },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1300, right: 1300 } } }, children: C }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync('HIPAA-Penetration-Testing-DiseaseFix.docx', buf); console.log('Wrote docx', buf.length, 'bytes'); });
