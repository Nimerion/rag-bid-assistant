import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

docs_data = [
    {
        "filename": "SEC-001_Data_Classification_and_Handling_Policy.pdf",
        "title": "Data Classification & Handling Standard",
        "doc_id": "POL-SEC-2026-01",
        "author": "Information Security & Compliance",
        "date": "15 January 2026",
        "content": [
            ("Policy Overview", "This document defines organizational data classification tiers to ensure appropriate operational and cryptographic controls across cloud and on-premises environments."),
            ("Classification Tiers", "Data is categorized into four distinct levels: Public (open distribution), Internal (staff access by default), Confidential (restricted access requiring role-based authorization), and Restricted (strictly segmented data including PII, credentials, and cryptographic keys)."),
            ("Encryption Standards", "Data at rest classified as Confidential or Restricted must use AES-256 encryption. Data in transit requires TLS 1.3 across all perimeter and inter-service boundaries."),
            ("Retention & Disposal", "Restricted customer telemetry must be purged after 90 days unless subject to legal hold. Decommissioned physical media requires cryptographic erasure and certified degaussing.")
        ]
    },
    {
        "filename": "SEC-002_Identity_and_Access_Management_Architecture.pdf",
        "title": "Enterprise Identity & Access Management (IAM) Standard",
        "doc_id": "ARCH-SEC-2026-04",
        "author": "Cloud Infrastructure Security",
        "date": "02 February 2026",
        "content": [
            ("Core Principles", "All corporate access operates under the Principle of Least Privilege (PoLP) and Zero Trust Architecture (ZTA). Network perimeter location confers zero baseline trust."),
            ("Multi-Factor Authentication", "Phishing-resistant FIDO2/WebAuthn hardware tokens or managed authenticator applications are mandatory for all production cloud consoles and code repositories."),
            ("Privileged Access Management (PAM)", "Permanent administrative access is prohibited. Production infrastructure credentials must be provisioned via Just-In-Time (JIT) access broker with automatic revocation after four hours."),
            ("Quarterly Access Reviews", "Department heads must review and certify entitlements for all direct reports every 90 days. Uncertified roles are revoked automatically at day 95.")
        ]
    },
    {
        "filename": "OPS-001_Production_Incident_Response_Playbook.pdf",
        "title": "Production Incident Management & Escalation Playbook",
        "doc_id": "SOP-OPS-2026-11",
        "author": "Site Reliability Engineering",
        "date": "18 February 2026",
        "content": [
            ("Incident Severities", "Severity 1 (Critical): Total service outage impacting >15% of active users. Severity 2 (Major): Core feature degradation with no immediate workaround. Severity 3 (Minor): Non-blocking operational issue."),
            ("SLA & Response Times", "Sev-1 incidents require incident commander assignment within 5 minutes and an executive status page update within 15 minutes. Sev-2 incidents require response within 30 minutes."),
            ("War Room Protocol", "The primary Incident Commander (IC) owns communication and delegation. Engineers must not execute ad-hoc production changes without IC logging."),
            ("Post-Mortem Requirements", "A blameless post-mortem must be scheduled within 72 hours of incident resolution for all Sev-1 and Sev-2 events. Action items must be logged in the engineering backlog within 5 business days.")
        ]
    },
    {
        "filename": "ENG-001_API_Design_and_Integration_Guidelines.pdf",
        "title": "REST and GraphQL API Engineering Guidelines",
        "doc_id": "ENG-ARCH-2026-02",
        "author": "Architecture Review Board",
        "date": "10 March 2026",
        "content": [
            ("API Versioning", "All public endpoints must expose major version paths (e.g., /api/v2/orders). Breaking changes without 180 days advance deprecation notification are strictly forbidden."),
            ("Pagination & Throttling", "Endpoints returning collections must enforce cursor-based pagination with a maximum default limit of 100 items. Default client rate limits are 1,200 requests per minute per authenticated client ID."),
            ("Payload & Schema Validation", "All inbound payloads must be strictly validated against OpenAPI 3.1 schemas. Additional unmapped JSON fields must be rejected with HTTP 422 Unprocessable Content."),
            ("Idempotency", "Mutating operations (POST/PATCH) handling financial transactions or inventory mutations must require an Idempotency-Key HTTP header valid for 24 hours.")
        ]
    },
    {
        "filename": "HR-001_Remote_Work_and_Equipment_Policy.pdf",
        "title": "Global Distributed Work & Hardware Policy",
        "doc_id": "HR-POL-2026-08",
        "author": "People Operations",
        "date": "04 January 2026",
        "content": [
            ("Eligibility", "Employees in qualifying technical and professional roles may work remotely up to 100% of their contracted hours, subject to manager agreement and local tax compliance."),
            ("Hardware Provisioning", "The company provides a standard corporate laptop, external monitor, and a one-time home office setup stipend of 750 GBP (or local equivalent). Personal hardware cannot connect to production systems."),
            ("Working Across Jurisdictions", "Employees may work from an approved secondary country for up to 30 calendar days per rolling 12 months, provided no corporate tax permanent establishment risk is created."),
            ("Core Working Hours", "To support synchronous collaboration across distributed teams, core working hours are established between 10:00 and 15:00 in the primary operating time zone of the team.")
        ]
    },
    {
        "filename": "FIN-001_Travel_and_Expense_Reimbursement_Policy.pdf",
        "title": "Corporate Travel & Expense Reimbursement Policy",
        "doc_id": "FIN-POL-2026-03",
        "author": "Finance & Procurement",
        "date": "12 February 2026",
        "content": [
            ("Pre-Approval Thresholds", "Domestic business travel exceeding 500 GBP and all international travel require written pre-approval from the functional Vice President prior to ticket issuance."),
            ("Air Travel & Rail Class", "Economy class is mandatory for flights under 6 hours duration. Premium Economy or Business Class is permitted for continuous international flights exceeding 6 hours."),
            ("Daily Subsistence Rates", "Subsistence caps are established at 75 GBP per day for domestic travel and 100 GBP (or local currency equivalent) for designated Tier 1 metropolitan locations."),
            ("Submission Windows", "Expense claims must be submitted via the expense portal within 30 days of trip completion, accompanied by itemized VAT receipts. Credit card counterfoils alone are insufficient.")
        ]
    },
    {
        "filename": "SRE-001_Disaster_Recovery_and_BCP_Plan.pdf",
        "title": "Disaster Recovery & Business Continuity Framework",
        "doc_id": "BCP-SRE-2026-05",
        "author": "Infrastructure Reliability Directorate",
        "date": "24 February 2026",
        "content": [
            ("Target RTO and RPO", "Tier 0 Critical Services (Authentication, Core Database) mandate a Recovery Point Objective (RPO) of <= 5 minutes and Recovery Time Objective (RTO) of <= 30 minutes."),
            ("Multi-Region Strategy", "Production databases operate cross-region asynchronous active-passive replication with automated failover triggers evaluated by synthetic heartbeat monitors."),
            ("Backup Frequency & Immutable Vaults", "Full database snapshots are generated every 24 hours, with transaction log archiving every 15 minutes. Backups are stored in WORM-compliant immutable object storage across secondary availability zones."),
            ("Annual DR Drills", "Live cross-region DR game days are executed bi-annually. The simulation involves simulated primary region isolation and must pass without data loss or SLA breach.")
        ]
    },
    {
        "filename": "COMP-001_Vendor_Risk_Management_Standard.pdf",
        "title": "Third-Party Vendor Risk Assessment Standard",
        "doc_id": "COMP-VRM-2026-07",
        "author": "Legal & Risk Governance",
        "date": "08 March 2026",
        "content": [
            ("Vendor Tiers", "Vendors processing customer data are Tier 1 (High Risk). Vendors providing corporate software without customer data access are Tier 2 (Moderate Risk). Operational suppliers are Tier 3 (Low Risk)."),
            ("Due Diligence Requirements", "Tier 1 vendors must furnish an unmodified SOC 2 Type II report completed within the preceding 12 months, along with an active ISO 27001 certificate and recent external penetration test summary."),
            ("Contractual Safeguards", "All vendor agreements handling company intellectual property or personal data must execute the standard Data Processing Addendum (DPA) containing standard contractual clauses (SCCs)."),
            ("Re-certification Frequency", "High-risk Tier 1 vendors undergo mandatory security and financial reassessments every 12 months. Failure to remediate identified security findings within 60 days results in termination.")
        ]
    },
    {
        "filename": "AI-001_Enterprise_Generative_AI_Usage_Policy.pdf",
        "title": "Enterprise Generative AI & Model Deployment Policy",
        "doc_id": "GOV-AI-2026-01",
        "author": "AI Governance Council",
        "date": "19 January 2026",
        "content": [
            ("Approved Model Services", "Employees may only use corporate-sanctioned generative AI gateways configured with zero-data-retention agreements. Public consumer generative AI tools are strictly prohibited for corporate data."),
            ("Customer & Proprietary Data", "Submitting source code, proprietary algorithms, or non-anonymized customer personal identifiable information (PII) to non-isolated external LLM endpoints constitutes a security violation."),
            ("Code Review Mandate", "All software code generated or augmented by LLM tools must undergo standard peer code review, static code analysis (SAST), and unit test validation prior to merging to main."),
            ("Model Hallucination & Risk Mitigation", "AI-assisted outputs utilized in regulatory submissions, financial forecasts, or HR hiring decisions must include deterministic verification and sign-off by a designated human subject matter expert.")
        ]
    },
    {
        "filename": "SEC-003_Vulnerability_Disclosure_and_Patch_Management.pdf",
        "title": "Vulnerability Assessment & Patch Management Standard",
        "doc_id": "SEC-PATCH-2026-09",
        "author": "Cyber Threat & Vulnerability Management",
        "date": "14 March 2026",
        "content": [
            ("Vulnerability Severity Levels", "Common Vulnerability Scoring System (CVSS v3.1) scores dictate urgency: Critical (CVSS 9.0-10.0), High (CVSS 7.0-8.9), Medium (CVSS 4.0-6.9), and Low (CVSS 0.1-3.9)."),
            ("Remediation Timeframes", "Critical vulnerabilities in internet-facing infrastructure must be remediated or mitigated within 48 hours of public patch availability. High vulnerabilities require remediation within 14 days."),
            ("Continuous Scanning", "Container registries and virtual machine golden images are scanned continuously. Builds containing unpatched Critical CVEs are blocked automatically at the CI/CD pipeline gate."),
            ("Bug Bounty Policy", "External security researchers are rewarded according to established impact matrices. Coordinated disclosure policy requires researchers to allow 90 days for internal remediation prior to public disclosure.")
        ]
    }
]

output_dir = "./rag_docs"
os.makedirs(output_dir, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1E293B'), spaceAfter=6)
meta_style = ParagraphStyle('DocMeta', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#64748B'), spaceAfter=12)
section_head = ParagraphStyle('SecHead', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle('SecBody', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'), spaceAfter=6)

for doc in docs_data:
    file_path = os.path.join(output_dir, doc["filename"])
    doc_template = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    story.append(Paragraph(doc["title"], title_style))
    story.append(Paragraph(f"<b>Document ID:</b> {doc['doc_id']} | <b>Owner:</b> {doc['author']} | <b>Date:</b> {doc['date']}", meta_style))
    story.append(Spacer(1, 4))
    divider = Table([['']], colWidths=[532], rowHeights=[1.5])
    divider.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0284C7'))]))
    story.append(divider)
    story.append(Spacer(1, 8))
    for sec_title, sec_body in doc["content"]:
        story.append(Paragraph(sec_title, section_head))
        story.append(Paragraph(sec_body, body_style))
    doc_template.build(story)

print(f"Successfully generated {len(docs_data)} PDF files in {output_dir}")
