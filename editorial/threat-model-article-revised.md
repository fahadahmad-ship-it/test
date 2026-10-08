# What a Medical Device Threat Model Looks Like in Practice

On a hospital ward, an infusion pump is a box on a pole. On a network diagram,
it is something else: a computer that accepts configuration data from a clinical
information system, runs third-party software it did not write, may be serviced
remotely by its manufacturer, and shares a network with several thousand devices
of unknown hygiene — including, often, the ones nobody has patched since
installation.

That gap between the two views is the reason threat modeling has moved from a
security-team exercise to a regulatory expectation. The FDA's current premarket
guidance, *Cybersecurity in Medical Devices: Quality Management System
Considerations and Content of Premarket Submissions*, issued February 3, 2026,
recommends that manufacturers use threat modeling to inform their cybersecurity
risk analysis, apply it across the whole medical device system, and do so
throughout the design process rather than at the end of it. That document
superseded the June 2025 version to align with the Quality Management System
Regulation, which took effect the day before it published — a detail worth
noting, because it signals where the agency filed the subject. Device security
is being treated as a quality-system obligation, not a security annex.

What a threat model is supposed to produce, though, is less obvious than the
requirement to have one. In practice it is not a diagram. It is a set of
answers: what the device connects to, who can interact with it, what is worth
protecting, and what happens if someone changes, blocks, observes, or replays
information in transit. The useful ones end somewhere specific — a design
change, a requirement, a test. The unhelpful ones end in a PDF.

## The device is a system, and the system is bigger than the device

The first decision is what is being modeled, and it is where most models are
quietly too small.

A connected patient monitor is rarely just a monitor. It is embedded software
and firmware, an operating system with its own supply chain, wireless and wired
interfaces, a central station, a clinical workstation, an update server,
possibly a cloud service and a mobile app, a remote service connection, and the
credentials that govern all of it. The model has to draw a boundary around that
whole arrangement and show how the parts talk to each other.

The FDA's guidance asks for something specific here: that the model cover all
medical device system elements, and that assumptions about the environment of
use be written down. The second half does more work than it appears to. A model
that assumes the hospital network is trustworthy will produce a short, calm list
of threats. The same device modeled on the assumption that an adversary is
already on that network — which is the assumption most hospital security teams
now operate under — produces a longer and less comfortable one. Neither model is
wrong about the device. They disagree about the world, and that disagreement is
usually implicit, which is exactly why the agency wants it stated.

## Assets, entry points, and the places where assumptions change

Once the system is drawn, the question is what an attacker would actually want
to reach.

In a medical device, the valuable asset is often not confidential at all. A
patient record matters, but so does a treatment parameter, a firmware image, a
calibration constant, a signing key, an audit log, or any value that determines
how the device behaves. Some assets need protecting because disclosure harms
someone. Others need protecting because modification does — and those are the
ones that connect most directly to safety.

The routes in are mundane and numerous: Ethernet, Wi-Fi, Bluetooth, USB, serial
and diagnostic ports, removable media, APIs, web interfaces, mobile
applications, cloud endpoints, service tools. Each one raises the same handful
of questions about authentication, authorization, input validation, encryption,
and update integrity. The interfaces that get missed tend to be the ones
invisible during clinical use — the maintenance port behind a panel, the service
laptop that plugs into it, the technician account with privileges nobody has
audited since the device shipped.

Trust boundaries are where the analysis earns its keep, because they mark the
points where assumptions change hands: data leaving a controlled component for
an uncontrolled one, a device accepting an instruction from another system, a
software update arriving from outside, a service engineer invoking privileged
functions. ANSI/AAMI SW96:2023, which the FDA recognized as a consensus standard
in 2023, organizes security risk management around much the same elements —
assets, threats, vulnerabilities, controls, and supply-chain relationships —
across design, production, and post-production.

## From "it could be hacked" to a scenario with a consequence

A threat model becomes useful at the point where it stops describing categories
and starts describing events.

"The device could be hacked" is not a finding; it is an anxiety. A scenario has
an actor, a path, and an outcome: someone on the hospital network impersonates
the system authorized to send configuration data to an infusion pump, and
changes a dose-limit value. Stated that way, the analysis can continue to the
part that matters. Would the altered value change what the pump does? Would the
pump validate the instruction, or accept it because it arrived on the expected
port? Would anyone see it? Would a nurse's independent check catch it, and is it
reasonable to rely on that?

This is the step that separates medical device threat modeling from the generic
version. The FDA's postmarket guidance treats threat modeling as a tool for
assessing exploitability and potential patient harm, and distinguishes
vulnerabilities by the severity of the harm that could follow. A flaw in a
non-critical display and a flaw in medication delivery are not the same finding
even if they share a CVSS score.

The historical record gives the exercise its weight. In 2015 the FDA issued a
safety communication recommending that hospitals stop using the Hospira Symbiq
infusion system after researchers showed its drug library could be altered over
the network. In 2017, roughly 465,000 Abbott cardiac devices required a firmware
update to close vulnerabilities that could have allowed unauthorized commands to
an implanted pacemaker. No patient harm was reported in either case. But both
began as the kind of scenario a threat model is supposed to surface before a
device ships, and both ended as something considerably more expensive.

## What the model is supposed to change

An analysis that identifies command injection as a credible threat should
produce something: authentication on the interface, authorization checks,
message integrity protection, input validation, or a refusal to execute commands
outside safe bounds. If the concern is a tampered update, the answer tends to be
secure boot, signed images, integrity verification, and rollback protection. The
test of a threat model is whether anything in the design is different because of
it.

Proportionality is the harder discipline. Not every theoretical threat deserves
a control, and a control that degrades clinical use can create a safety problem
of its own. A lock screen that defends a bedside monitor against a plausible
adversary and also costs a clinician fifteen seconds during a code is not an
unambiguous improvement. Security on a medical device competes with
availability, usability, performance, and serviceability, and the resolution of
that competition is itself a safety decision. This is the argument for modeling
early: the trade-offs are cheap to make in architecture and expensive to make in
validation.

The practical output is a chain that holds up when someone pulls on it — from
scenario, to requirement, to implemented control, to evidence that the control
works. The FDA's guidance frames this as using threat modeling to inform both
pre- and post-mitigation risk assessment, which only means anything if the
before and after are traceable to the same analysis.

## It does not end at clearance

A device ships into a world that keeps moving. Dependencies acquire
vulnerabilities, attack techniques get cheaper, hospital infrastructure is
replaced, service models change. The URGENT/11 vulnerabilities disclosed in 2019
affected a widely used network stack embedded in devices whose manufacturers had
not written it and, in some cases, did not know they were carrying it. No
premarket analysis could have named that flaw. A model with a current component
inventory and traceable mitigations can at least answer, within days, which
products are affected.

That is what traceability buys. If a threat is linked to the asset it touches,
the interface it arrives through, the potential patient impact, the mitigation
chosen, and the evidence behind it, then a change — a replaced component, a new
radio, a new remote-service pathway — points to the specific parts of the model
that need revisiting. Without those links, every change reopens everything, and
in practice that means nothing gets reopened.

## The test of a good one

A reasonable measure of a threat model is whether anyone outside the security
team can use it. A product engineer should be able to see which design decisions
are security-relevant. A quality team should see where cybersecurity risk meets
the rest of risk management. A regulatory reviewer should be able to find the
evidence behind a claim. A clinical stakeholder should be able to follow why a
particular threat matters at the bedside.

That is becoming harder as devices absorb more software, more connectivity, more
third-party components, and machine-learning functionality whose failure modes
are still being worked out — an area the FDA's standards recognition has begun
to address separately.

Which argues for smaller rather than larger. A clear architecture diagram, a
written statement of what the manufacturer assumes about the environment, a set
of scenarios with consequences attached, and mitigations that can be traced to
evidence will do more than a hundred pages of security vocabulary. The point of
the exercise is not to anticipate every attack; nobody can. It is to know which
paths into the device are real, what they would cost if someone took them, and
to be able to show why the chosen defenses were enough — before the question is
asked by someone outside the company.
