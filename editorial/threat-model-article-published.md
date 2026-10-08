# What a medical device threat model looks like in practice

On a hospital ward, an infusion pump is a box on a pole. On a network diagram it
is something else: a computer that accepts configuration data from a clinical
information system, runs third party software it did not write, may be serviced
remotely by its manufacturer, and shares a network with several thousand other
devices of unknown hygiene, including the ones nobody has patched since
installation.

That gap between the two views is why threat modeling has moved from a security
team exercise to a regulatory expectation. The FDA's current premarket guidance,
*Cybersecurity in Medical Devices: Quality Management System Considerations and
Content of Premarket Submissions*, issued on February 3, 2026, recommends that
manufacturers use threat modeling to inform cybersecurity risk analysis, apply
it across all elements of the medical device system, and carry it through the
design process rather than attach it at the end. That version superseded the
June 2025 guidance in order to align with the Quality Management System
Regulation, which took effect on February 2, 2026, one day before the guidance
published. The timing is worth noticing. It tells you where the agency has filed
the subject: device security is a quality system obligation, not a security
annex.

What a threat model should actually produce is less obvious than the expectation
that one exists. It is not a diagram. It is a set of answers to plain questions.
What can the device connect to? Who can interact with it? What is worth
protecting? What happens if someone alters, blocks, observes, or replays
information in transit? The useful models end somewhere specific, in a design
change, a requirement, or a test. The unhelpful ones end in a PDF.

## Start by drawing the system, not the device

The first decision is what is being modeled, and it is where most models are
quietly too small.

A connected patient monitor is rarely just a monitor. It is embedded software
and firmware, an operating system with a supply chain of its own, wireless and
wired interfaces, a central station, a clinical workstation, an update server,
possibly a cloud service and a mobile application, a remote service connection,
and the credentials governing all of it. The model has to draw a boundary around
that whole arrangement and show how the parts communicate.

The FDA guidance asks for two things here: that the model cover all medical
device system elements, and that assumptions about the environment of use be
documented explicitly. The second does more work than it appears to. A model
that assumes the hospital network is trustworthy produces a short and reassuring
list of threats. The same device modeled on the assumption that an adversary
already has a foothold on that network, which is how most hospital security
teams now operate, produces a longer and far less comfortable one. Neither model
is wrong about the device. They disagree about the world, and that disagreement
usually goes unstated, which is precisely why the agency wants it written down.

## Identify the assets, the ways in, and the trust boundaries

Once the system is drawn, the question becomes what an attacker would want to
reach.

In a medical device the valuable asset is often not confidential at all. Patient
data matters, but so does a treatment parameter, a firmware image, a calibration
constant, a signing key, an audit log, or any stored value that determines how
the device behaves. Some assets need protection because disclosure harms
someone. Others need protection because modification does, and those are the
ones that run straight into patient safety.

The routes in are mundane and numerous: Ethernet, Wi-Fi, Bluetooth, USB, serial
and diagnostic ports, removable media, APIs, web interfaces, mobile
applications, cloud endpoints, service tools. Each raises the same small set of
questions about authentication, authorization, input validation, encryption and
update integrity. The interfaces most often missed are the ones invisible during
clinical use: the maintenance port behind a panel, the service laptop that plugs
into it, the technician account with standing privileges that nobody has audited
since the device shipped.

Trust boundaries are where the analysis earns its keep, because they mark the
points at which assumptions change hands. Data leaves a controlled component for
an uncontrolled one. A device accepts an instruction from another system. A
software update arrives from outside. A service engineer invokes privileged
functions. ANSI/AAMI SW96:2023, which the FDA recognized as a consensus standard
in 2023, organizes security risk management around the same elements, covering
assets, threats, vulnerabilities, controls and supply chain relationships across
design, production and post production.

## Write scenarios, not categories

A threat model becomes useful at the point where it stops naming categories and
starts describing events.

"The device could be hacked" is not a finding. It is an anxiety. A scenario has
an actor, a path and an outcome. Someone on the hospital network impersonates
the system authorized to send configuration data to an infusion pump and changes
a dose limit. Stated that way, the analysis can continue into the part that
matters. Would the altered value change what the pump does? Would the pump
validate the instruction, or accept it because it arrived on the expected port?
Would anyone see it? Would a nurse's independent check catch it, and is it
defensible to rely on that?

This is the step that separates medical device threat modeling from the generic
kind. The FDA's 2016 postmarket guidance evaluates vulnerabilities by their
exploitability and by the severity of the patient harm that could result, which
means a flaw in a secondary display and a flaw in medication delivery are not
the same finding even when they share a severity score.

The record gives the exercise its weight. On July 31, 2015 the FDA issued a
safety communication strongly encouraging hospitals to move off the Hospira
Symbiq infusion system, after it was confirmed that the pump could be reached
through a hospital network and its dosage altered by an unauthorized user. It
was the first time the agency had urged facilities to transition away from a
device over a cybersecurity flaw. Two years later, in August 2017, the FDA
approved a firmware update for radio frequency enabled pacemakers made by Abbott,
formerly St. Jude Medical, and classified it as a recall. The vulnerabilities
could have let someone other than the treating physician reach an implanted
device with commercially available equipment and modify its programming, with
rapid battery depletion or inappropriate pacing as the potential results.
Contemporaneous reporting put the affected population at roughly 465,000
patients. Neither case produced a confirmed instance of patient harm. Both began
as the kind of scenario a threat model exists to surface, and both ended as
something considerably more expensive than a design change.

## Let the model change the design

An analysis that identifies command injection as a credible threat should
produce something: authentication on the interface, authorization checks,
message integrity protection, input validation, or a refusal to execute commands
outside safe bounds. If the concern is a tampered update, the answers tend to be
secure boot, signed images, integrity verification and rollback protection. The
test of a threat model is whether anything about the design is different because
it was done.

Proportionality is the harder discipline. Not every theoretical threat deserves
a control, and a control that degrades clinical use can introduce a safety
problem of its own. A lock screen that defends a bedside monitor against a
plausible adversary and also costs a clinician fifteen seconds during a code is
not an unambiguous improvement. Security on a medical device competes with
availability, usability, performance and serviceability, and resolving that
competition is itself a safety decision. It is a version of a wider lesson in
hospital operations, where [resilience depends as much on workflow as on new
hardware](https://medicalnewsbulletin.com/why-healthcares-resilience-depends-on-unsung-operational-innovations/). It is also the strongest argument for
modeling early, because those trade offs are cheap to make in architecture and
expensive to make in validation.

The practical output is a chain that holds when somebody pulls on it, running
from scenario to requirement to implemented control to evidence that the control
works. The FDA guidance frames this as using threat modeling to inform both pre
mitigation and post mitigation risk assessment, which only means something if
the before and the after trace back to the same analysis. Published frameworks
for [Medical Device Threat Modeling](https://bluegoatcyber.com/services/threat-modeling-services) set out the sequence in
more detail, and the discipline is largely in maintaining those links rather
than in generating the initial list.

## Keep it alive after clearance

A device ships into a world that keeps moving. Dependencies acquire
vulnerabilities, attack techniques get cheaper, hospital infrastructure is
replaced, service models change.

On October 1, 2019 the FDA warned about URGENT/11, a set of eleven
vulnerabilities in IPnet, a networking component licensed into several real time
operating systems used in medical devices. The original developer no longer
supported the component, exploit code was already public, and affected products
identified at the time included an imaging system, an infusion pump and an
anesthesia machine. More than thirty manufacturers eventually issued their own
advisories. No premarket analysis could have named that flaw in advance. What a
manufacturer needed on the day it was disclosed was the ability to answer a
narrower question quickly: do our products contain this component, and where.

That is what traceability buys. When a threat is linked to the asset it touches,
the interface it arrives through, the potential patient impact, the mitigation
selected and the evidence behind it, a change points to the specific parts of
the model that need revisiting. Add a radio, swap a component, open a new remote
service pathway, and the affected analysis is identifiable. Without those links
every change reopens everything, which in practice means nothing gets reopened
at all.

## The test of a good one

A fair measure of a threat model is whether anyone outside the security team can
use it. A product engineer should be able to see which design decisions are
security relevant. A quality team should see where cybersecurity risk meets the
rest of risk management. A regulatory reviewer should be able to find the
evidence behind a claim. A clinician should be able to follow why a given threat
matters at the bedside. The problem is familiar from public health, where
[analysis only changes outcomes once it reaches the people who act on it](https://medicalnewsbulletin.com/how-epidemiologists-turn-research-into-public-health-action).

That is getting harder as [devices absorb more software, more connectivity](https://medicalnewsbulletin.com/cutting-edge-breakthroughs-in-medical-technology-the-devices-and-innovations-revolutionizing-healthcare/),
more third party components and machine learning functionality whose failure
modes are still being worked out, an area the FDA's standards recognition has begun to
address separately.

All of which argues for smaller rather than larger. A clear architecture
diagram, a written statement of what the manufacturer assumes about the
environment, a set of scenarios with consequences attached, and mitigations
traceable to evidence will do more than a hundred pages of security vocabulary.
The point is not to anticipate every attack, because nobody can. It is to know
which paths into the device are real, what they would cost if someone took them,
and to be able to show why the chosen defenses were enough, before that question
is asked by somebody outside the company.
