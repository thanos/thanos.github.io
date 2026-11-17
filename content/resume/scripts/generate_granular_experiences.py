#!/usr/bin/env python3
"""Generate granular experience atoms + EXPERIENCES-REVIEW.{csv,md} from screenshots/old resumes."""
from __future__ import annotations

from pathlib import Path
import csv
import yaml

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiences"
REVIEW_CSV = ROOT / "EXPERIENCES-REVIEW.csv"
REVIEW_MD = ROOT / "EXPERIENCES-REVIEW.md"
TODAY = "2026-11-16"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def dump_atom(d: dict) -> Path:
    order = [
        "id", "kind", "title", "client", "org", "job", "role", "responsible",
        "when", "summary", "bullets", "domain", "skills", "signals",
        "proof", "provenance", "visibility",
    ]
    out = {k: d[k] for k in order if k in d and d[k] is not None}
    for k, v in d.items():
        if k not in out and not k.startswith("_") and v is not None:
            out[k] = v
    path = EXP / f"{out['id']}.yaml"
    path.write_text(
        yaml.dump(
            out,
            Dumper=NoAliasDumper,
            sort_keys=False,
            allow_unicode=True,
            width=100,
            default_flow_style=False,
        )
    )
    return path


def A(**kw):
    signals = kw.pop("signals", None)
    domain = kw.pop("domain", ["finance"])
    skills = kw.pop("skills", [])
    d = {
        "id": kw["id"],
        "kind": kw.get("kind", "built"),
        "title": kw["title"],
        "client": kw.get("client"),
        "org": kw.get("org"),
        "job": kw.get("job"),
        "when": {"start": kw["start"], "end": kw.get("end")},
        "summary": kw["summary"],
        "bullets": kw["bullets"],
        "domain": domain,
        "skills": skills,
        "signals": signals
        or {
            "domains": domain,
            "skills": [s.lower().replace(" ", "-") for s in skills]
            + (kw.get("extra_signals") or ["architecture"]),
            "seniority": kw.get("seniority", "hybrid"),
            "impact": kw.get("impact", ["platform"]),
        },
        "proof": kw.get(
            "proof", {"metrics": [], "links": [], "source": kw.get("source", "job")}
        ),
        "provenance": {
            "type": kw.get("prov_type", "job_built"),
            "refs": kw.get(
                "refs",
                [
                    {"path": "content/resume/old_resumes/resume-incomplete.txt"},
                    {"path": "content/resume/old_resumes/resume-2025.txt"},
                    {"path": "content/resume/screenshots"},
                ],
            ),
            "last_verified": TODAY,
        },
        "visibility": kw.get("visibility", "public"),
        "_status": kw.get("status", "new"),
        "_split_from": kw.get("split_from"),
        "_source": kw.get("from_source", "screenshots+old_resumes"),
    }
    if kw.get("responsible"):
        d["responsible"] = kw["responsible"]
    if kw.get("role"):
        d["role"] = kw["role"]
    return d


ATOMS: list[dict] = []


def add(**kw):
    ATOMS.append(A(**kw))


# =============================================================================
# RBC — STS / platform products (screenshots + old resumes)
# =============================================================================
add(
    id="rbc-sts",
    title="Shared Technical Services (STS) — AWS-like on-prem platform",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    kind="ran",
    responsible=["architected", "run"],
    summary="Cloud-agnostic, scalable collection of AWS-like shared technical services.",
    bullets=[
        "Built and ran STS — AWS-like services that are cloud-agnostic and scalable.",
        "Included on-prem replicas of SNS, SQS, Lambda (FaaS), S3-like storage, auth/permission, discovery and connectivity.",
    ],
    skills=["Python", "Elixir"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-sns",
    title="Simple Notification Service (SNS)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2017,
    responsible=["built", "architected", "run"],
    summary="Platform-agnostic AWS-SNS-style notification; 65+ app codes / 92+ applications.",
    bullets=[
        "Architected and coded SNS modeled on AWS SNS, on-prem and on bank cloud.",
        "Grew to 65+ app codes in production and eventually 92+ applications.",
    ],
    skills=["Python"],
    proof={
        "metrics": [
            {"label": "applications", "value": 92},
            {"label": "app_codes", "value": 65},
        ],
        "links": [],
        "source": "job",
    },
    split_from="rbc-faas-notification",
)
add(
    id="rbc-faas",
    title="On-prem Function-as-a-Service (Lambda)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2017,
    end=2018,
    responsible=["built", "architected"],
    summary="Forked OpenWhisk into bank FaaS, then rewrote with streamed-event triggers.",
    bullets=[
        "POC then forked IBM OpenWhisk and adapted it on-prem/cloud as RBC’s Lambda-style FaaS.",
        "Rewrote from scratch with streamed-event triggers to cut microservice sprawl and RTB cost.",
    ],
    skills=["Python", "Erlang"],
    split_from="rbc-faas-notification",
)
add(
    id="rbc-idol",
    title="IDOL — next-gen single execution platform (FaaS)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    responsible=["architected"],
    summary="Strategic BCST initiative: single execution platform — new FaaS called IDOL.",
    bullets=[
        "Drove IDOL as the next-generation single execution platform (successor to on-prem FaaS) for BCST.",
    ],
)
add(
    id="rbc-rabacus",
    title="RABACUS — one browser for all the Bank’s data",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected", "run"],
    summary="Internal Tableau-alternative visual portal to bank data.",
    bullets=[
        "Delivered RABACUS as the visual portal to bank data — an internal Tableau alternative.",
        "Clients: BCS (ECPT/P2M), DADT (BookBuilder, DataWatch), GELP, RAMPP (Workspaces), Risk IT and Finance IT.",
    ],
    skills=["Python", "TypeScript"],
)
add(
    id="rbc-rabacus-studio",
    title="RABACUS Studio — dashboard builder for backend developers",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    responsible=["built", "architected"],
    summary="GELP-sponsored tool so backend developers without web skills can ship professional UIs.",
    bullets=[
        "POC’d then productized a web framework so programmers with no web knowledge can build dashboards, reporting, and trading screens in minutes.",
        "Became core technology behind new UI development; sponsored by GELP as RABACUS Studio.",
    ],
    skills=["Python", "TypeScript", "Node"],
)
add(
    id="rbc-workspaces",
    title="WORKSPACES — multi-tenant hierarchical metadata API",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected", "run"],
    summary="Multi-tenant API for managing hierarchical metadata (RAMPP Workspaces).",
    bullets=[
        "Delivered WORKSPACES — multi-tenant API for hierarchical meta-data, used by RAMPP and RABACUS clients.",
    ],
    skills=["Python"],
)
add(
    id="rbc-pitos",
    title="PITOS — point-in-time object store",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2017,
    responsible=["built", "architected", "run"],
    summary="Athena/Quartz-style low-latency trading data fabric / point-in-time object store.",
    bullets=[
        "Coded the original POC and built PITOS — scalable low-latency fabric for large-scale trading data.",
        "Became the de-facto trading data store; integral to PRISM and new OMS designs.",
    ],
    skills=["Python", "Elixir"],
)
add(
    id="rbc-pitos-cache",
    title="PITOS cache — cross-VM cache for NextGen HA",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2022,
    responsible=["architected"],
    summary="Cross-VM PITOS cache for NextGen HA; ~$800k/yr license avoidance.",
    bullets=[
        "Delivered PITOS cache — a cross-VM cache for NextGen HA.",
        "Cited ~$800k/year license avoidance on nomination materials.",
    ],
    proof={
        "metrics": [{"label": "license_avoidance_usd_per_year", "value": 800000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-risk-api",
    title="RISK API — controlled enterprise data delivery",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected"],
    summary="Controlled, cost-efficient data delivery API to the Enterprise.",
    bullets=[
        "Delivered RISK API for controlled and cost-efficient delivery of data to the Enterprise.",
    ],
    skills=["Python"],
)
add(
    id="rbc-emds",
    title="EMDS — Enterprise Market Data Services",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected", "run"],
    summary="Quandl/Quantopian-like single source for market data and algorithm sandbox.",
    bullets=[
        "Built EMDS as the single source for market data, then central to the CM Data Strategy program.",
        "Positioned as a one-stop market-data shop and algorithm sandbox.",
    ],
    skills=["Python", "Elixir"],
    split_from="rbc-shared-data-services",
)
add(
    id="rbc-cmla",
    title="CMLA — enterprise centralized logging",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2017,
    responsible=["architected"],
    summary="Enterprise centralized logging service (CMLA / Central Logging).",
    bullets=[
        "Architected Central Logging / CMLA as the enterprise centralized logging service (2017).",
    ],
    skills=["Python", "Elixir"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-jupyter-hub",
    title="Jupyter Hub — quant development environment",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected", "run"],
    summary="Jupyter Hub environment for quant development on bank data/ML platforms.",
    bullets=[
        "Delivered Jupyter Hub as a quant development environment on shared technical services.",
    ],
    skills=["Python"],
)
add(
    id="rbc-ml-platform",
    title="Machine Learning Platform — governed model hosting",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected", "run"],
    summary="Secure, scalable ML model management / AI Ops platform for Capital Markets.",
    bullets=[
        "Architected the ML model management platform (AI Ops) with governance.",
        "Clients: Aiden, Client First, CreditAI, EMDS, GRA, GTI Data Science, GTO, Insurance, Munis, Quants.",
        "Estimated ~$600k saved per client onboarded; munis pricing was first production client.",
    ],
    skills=["Python", "Erlang"],
    domain=["finance", "AI"],
    proof={
        "metrics": [{"label": "savings_per_client_usd", "value": 600000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-sdi",
    title="SDI — Single Data Interface SDK",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected", "run"],
    summary="Single programmer interface / SDK to BCS data; ~$5–10MM / 5yr cost avoidance.",
    bullets=[
        "Delivered SDI — one interface to BCS data for efficiency and agility.",
        "Clients included Logan, NextGen, Thor.",
        "Nomination materials cite ~$5–10MM cost avoidance/savings over five years.",
    ],
    skills=["Python", "Elixir", "Rust"],
    proof={
        "metrics": [
            {"label": "cost_avoidance_usd_5yr_low", "value": 5000000},
            {"label": "cost_avoidance_usd_5yr_high", "value": 10000000},
        ],
        "links": [],
        "source": "job",
    },
    split_from="rbc-shared-data-services",
)
add(
    id="rbc-data-transport",
    title="One Data Transport — Kappa-style bank data fabric",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected"],
    summary="High-speed Kappa-style transport shipping bank data from logs to FRTB reports.",
    bullets=[
        "Built One Data Transport — Kappa-architecture transport/transform from logs through FRTB reports.",
    ],
    skills=["Elixir", "Python"],
    split_from="rbc-shared-data-services",
)
add(
    id="rbc-data-ingest",
    title="Single data ingest — RETE rules engine",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected"],
    summary="Generic RETE-based ingest consolidating 100+ separate ingest projects.",
    bullets=[
        "Built a generic RETE-based rules engine consolidating over one hundred separate ingest projects.",
    ],
    skills=["Python"],
    split_from="rbc-shared-data-services",
)
add(
    id="rbc-data-lake",
    title="Capital Markets Data Lake",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    responsible=["architected"],
    summary="Capital Markets Data Lake (2016).",
    bullets=["Delivered Capital Markets Data Lake (2016)."],
    skills=["Python"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-cm-data-registry",
    title="CM Data Registry",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected"],
    summary="Capital Markets data registry paired with data-lake / RABACUS industrialization.",
    bullets=[
        "Delivered CM Data Registry as part of the discoverable-data / RABACUS industrialization story.",
    ],
    skills=["Python"],
)
add(
    id="rbc-expense-reporting-portal",
    title="Expense Reporting Portal",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2022,
    responsible=["architected", "run"],
    summary="Dashboards governing 3rd-party and T&E spend (distinct from trade-expense invoices).",
    bullets=[
        "Delivered Expense Reporting Portal for T&E, Corporate Card, Overtime Meal, IT Professional Services, Mgmt Consulting, Supplier Risk.",
        "Clients: Central Funding, COO, Finance, FIC, Global Equities, GIB, Global Research.",
    ],
    skills=["Python"],
)
add(
    id="rbc-revort",
    title="REVORT — Broadridge capacity replacement",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    responsible=["architected", "run"],
    summary="REVORT replacing Broadridge for capacity; ~$270k/yr license avoidance.",
    bullets=[
        "Delivered REVORT as Broadridge replacement for capacity.",
        "Cited ~$270k/year license avoidance; related to equity settlement migration off Broadridge.",
    ],
    proof={
        "metrics": [{"label": "license_avoidance_usd_per_year", "value": 270000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-test-automation-bcst",
    title="Test Automation for BCST (EOD / T+1 industry testing)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    responsible=["architected"],
    summary="Automated EOD processes and industry testing for T+; ~15% cycle cut, ~$200k/yr.",
    bullets=[
        "Delivered Test Automation for BCST to automate EOD processes and industry testing for T+.",
        "Cited ~15% cycle-time reduction and ~$200k/year on nomination materials.",
    ],
    proof={
        "metrics": [{"label": "savings_usd_per_year", "value": 200000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-gla-reporting",
    title="GLA reporting & analytical platform",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    responsible=["architected"],
    summary="New reporting and analytical platform for GLA (strategic BCST initiative).",
    bullets=[
        "Drove a new reporting and analytical platform for GLA as a strategic BCST initiative.",
    ],
    skills=["Python"],
)
add(
    id="rbc-gms-supervisor-control",
    title="Single supervisor control service for GMS",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    responsible=["architected"],
    summary="Strategic BCST initiative: single supervisor control service for GMS.",
    bullets=[
        "Drove a single supervisor control service for Global Markets Supervision.",
    ],
    skills=["Python"],
    split_from="rbc-global-market-supervision",
)
add(
    id="rbc-cm-business-supervision",
    title="CM Business Supervision Controls",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    kind="ran",
    responsible=["architected", "run"],
    summary="CM Business Supervision Controls mandate (alongside GMS and Financial Controls).",
    bullets=[
        "Technical leadership for CM Business Supervision Controls under the expanded ops mandate.",
    ],
)
add(
    id="rbc-financial-controls",
    title="Financial Controls — technical transformation mandate",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    kind="ran",
    responsible=["architected", "run"],
    summary="Technical leadership/transformation for Financial Controls.",
    bullets=[
        "Provided technical leadership and transformation for Financial Controls (cost, transparency, reliability).",
    ],
)
add(
    id="rbc-t1-infrastructure",
    title="T+1 transaction processing infrastructure",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    end=2024,
    responsible=["built", "architected", "run"],
    summary="Designed, built, and owned the bank’s T+1 infrastructure including 15c6-2.",
    bullets=[
        "Designed, built, and owned T+1 transaction processing and post-trade services (2024).",
        "Contributed to core T+1 including Rule 15c6-2; STS/SDI/FaaS/test automation cut delivery from months to weeks.",
    ],
    skills=["Python", "Elixir"],
    split_from="rbc-shared-ops-services",
)
add(
    id="rbc-trade-repository",
    title="Central Trade Repository",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    responsible=["architected", "run"],
    summary="Trade Repository across CM, Wealth, and Cash Management.",
    bullets=[
        "Owned Trade Repository as a shared operations service across CM, Wealth, and Cash Management.",
        "Consolidated event-sourced trade events for trade-operations shared services.",
    ],
    skills=["Python"],
    split_from="rbc-shared-ops-services",
)
add(
    id="rbc-emac-cmacs",
    title="eMac / CMACS — Capital Markets access attestation",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    responsible=["architected"],
    summary="CM Technology Risk access/attestation (eMac/CMACS).",
    bullets=[
        "Delivered/supported CMACS (CM Technology Risk) alongside central access control.",
        "Nomination materials cite ~$500k projected impact for eMac-related work.",
    ],
    proof={
        "metrics": [{"label": "projected_usd", "value": 500000}],
        "links": [],
        "source": "job",
    },
    split_from="rbc-access-control",
)
add(
    id="rbc-mla-sentry",
    title="MLA & SENTRY — fast bug/defect tooling",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="MLA & SENTRY tooling — “zapping bugs fast” on nomination decks.",
    bullets=["Delivered MLA & SENTRY tooling to accelerate defect detection and resolution."],
)
add(
    id="rbc-containerization",
    title="Containerization program (Docker/K8s → AES)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    responsible=["architected"],
    summary="Advocated, POC’d, implemented containerization; divested to AES along maturity curve.",
    bullets=[
        "Advocated, POC’d, and implemented containerization (Docker/Kubernetes) in cookiecutters and STS.",
        "Divested the program to AES along the maturity curve.",
    ],
)
add(
    id="rbc-raas",
    title="Rules as a Service (RaaS)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="Airflow-inspired rules engine using FaaS execution and PITOS dependency graphs.",
    bullets=[
        "Architected RaaS based on Airflow patterns, using FaaS for execution and PITOS for dependency graphs.",
        "Integrated with the bank and used in eight projects.",
    ],
    skills=["Python"],
    proof={"metrics": [{"label": "projects", "value": 8}], "links": [], "source": "job"},
)
add(
    id="rbc-cookiecutters",
    title="Inner-sourced project cookiecutters / application framework",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    responsible=["architected"],
    summary="Cookiecutters blueprinting config, secrets, logging, CI/CD, containers, RTB at genesis.",
    bullets=[
        "Inner-sourced cookiecutters for configuration, secrets, logging, events, GitHub layout, makefiles, CI/CD, Docker/K8s, and RTB.",
        "Base layer of the Shared Technical Services “application framework” culture change.",
    ],
)
add(
    id="rbc-distributed-compute",
    title="Distributed Compute Service",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="Distributed Compute Service (2018).",
    bullets=["Architected Distributed Compute Service (2018)."],
    skills=["Python", "Elixir"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-trading-data-core",
    title="Real-time Trading Data Core (Athena-style)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="Real-time Trading Data Core in the Athena-style data ecosystem (2018).",
    bullets=["Built Real-time Trading Data Core (Athena-style, 2018)."],
    skills=["Python", "Elixir"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-position-pnl",
    title="Real-time Position and PnL systems",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2020,
    responsible=["architected"],
    summary="Real-time Position and PnL; event-sourcing framework as position service.",
    bullets=[
        "Delivered real-time Position and PnL systems (2020).",
        "Repurposed trading data-ecosystem codebase into a general event-sourcing / real-time position service.",
    ],
    skills=["Python"],
    split_from="rbc-ml-pricing",
)
add(
    id="rbc-tokenization-platform",
    title="Digital Asset Tokenization Platform",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2022,
    responsible=["architected"],
    summary="Tokenization platform covering issuance / primary / secondary.",
    bullets=[
        "Delivered tokenization platform (2022).",
        "Digital Asset Tokenization Platform PoC covering issuance / primary / secondary.",
    ],
    domain=["finance", "crypto"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-blockchain-ledger-poc",
    title="Blockchain-based ledger PoC / IBM Reference Ledger",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="Blockchain ledger PoC; distributed Reference Ledger with IBM and Canadian banks.",
    bullets=[
        "Blockchain-based ledger PoC for Capital Markets.",
        "Distributed Reference Ledger work with IBM and Canadian banks.",
        "Owned Blockchain Group that built an internal chain used as an immutable ledger.",
    ],
    domain=["finance", "crypto"],
)
add(
    id="rbc-blockchain-notes-poc",
    title="Notes trading platform PoC (blockchain)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    end=2016,
    responsible=["architected"],
    summary="Notes trading platform PoC on blockchain (2016).",
    bullets=["Built a notes trading platform PoC on the internal blockchain stack (2016)."],
    domain=["finance", "crypto"],
)
add(
    id="rbc-blockchain-muni-trading",
    title="Municipal bond trading platform (blockchain)",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2022,
    responsible=["architected", "run"],
    summary="Municipal bond trading platform on blockchain — production 3Q 2022.",
    bullets=[
        "Delivered municipal bond trading platform; in production 3rd quarter 2022 (Ethereum/Solidity/Vyper).",
    ],
    skills=["Solidity"],
    domain=["finance", "crypto", "trading"],
)
add(
    id="rbc-encompass-migration",
    title="Encompass commodities migration",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2014,
    responsible=["built"],
    summary="Commodities lead engineer for Encompass migration (~$4MM).",
    bullets=["Commodities lead engineer for Encompass migration (~$4MM migrate)."],
    proof={
        "metrics": [{"label": "migration_usd", "value": 4000000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-metals-financing",
    title="Metals Financing build-out",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2014,
    responsible=["built"],
    summary="Helped build out Metals Financing alongside Encompass commodities work.",
    bullets=["Helped build out Metals Financing for commodities."],
)
add(
    id="rbc-ib-pipeline",
    title="Investment Bank Pipeline analytics",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2015,
    responsible=["built"],
    summary="Automated IB pipeline analytics; Refine PoC precursor to RABACUS.",
    bullets=[
        "In 2015 automated the IB pipeline; principal tool was Tableau.",
        "POC’d Refine as a Tableau alternative that later informed RABACUS.",
    ],
    skills=["Python"],
)
add(
    id="rbc-nextgen-oms-poc",
    title="Next-gen Sales and Trading OMS PoC",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2017,
    responsible=["architected"],
    summary="Generic plug-and-play OMS on PITOS for the new cross-asset trading platform.",
    bullets=[
        "Designed a new generic OMS with plug-and-play architecture based on PITOS.",
        "Part of next-gen cross-asset trading infrastructure (multi-region, hot releases, five-nines targets).",
    ],
    skills=["Python"],
)
add(
    id="rbc-security-master",
    title="Universal Security Master",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="Temporal, cross-market and region universal Security Master for RBC.",
    bullets=[
        "Created a new temporal, cross-market and region universal Security Master for RBC.",
    ],
    skills=["Python"],
)
add(
    id="rbc-prism",
    title="PRISM data-storage initiative",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="PRISM data-storage initiative with PITOS as an integral component.",
    bullets=[
        "Advanced PRISM data-storage initiative; PITOS as an integral part.",
    ],
)
add(
    id="rbc-cross-asset-ui",
    title="Cross-asset trading UI platform",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    responsible=["architected", "run"],
    summary="Single cross-asset trading app replacing five systems and ~30 spreadsheets.",
    bullets=[
        "Built a single cross-asset trading application inspired by Bloomberg, Ikon, MetaTrader, and Quantopian.",
        "Replaced five trading systems and about thirty spreadsheet-based systems.",
    ],
    skills=["Python", "TypeScript"],
    proof={
        "metrics": [
            {"label": "systems_replaced", "value": 5},
            {"label": "spreadsheets_replaced", "value": 30},
        ],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-structured-flow-ops",
    title="Structured & Flow trade maintenance",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2019,
    kind="ran",
    responsible=["run"],
    summary="Owned Structured & Flow trade maintenance; RedHat 7 port ~$7MM operational savings.",
    bullets=[
        "Owned Structured & Flow trade maintenance and improvements.",
        "Refactoring and RedHat 7 port resulted in seven million operational savings.",
    ],
    proof={
        "metrics": [{"label": "operational_savings_usd", "value": 7000000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-hpc-nic-fpga",
    title="HPC messaging — BPF, DPDK, Smart NIC, FPGA",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2017,
    responsible=["architected"],
    summary="Userspace/BPF/DPDK/Smart NIC/FPGA work processing 60+ million messages/second.",
    bullets=[
        "Projects leveraging programmable NICs, DPDK, BPF, and FPGA-based routing/indexing.",
        "Processed 60+ million messages a second in userspace paths.",
    ],
    skills=["C", "C++"],
    proof={
        "metrics": [{"label": "messages_per_second", "value": 60000000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-frtb-aml",
    title="FRTB and AML infrastructure",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2018,
    responsible=["architected"],
    summary="FRTB and AML infrastructure (2018).",
    bullets=["Delivered FRTB and AML infrastructure (2018)."],
    skills=["Python"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-lme-openlink",
    title="LME trading platform / OpenLink migration",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2011,
    end=2012,
    responsible=["built"],
    summary="LME trading platform and OpenLink migration; commodities consolidation.",
    bullets=[
        "LME trading platform / OpenLink migration.",
        "As contractor (2011–2012): consolidated commodities trading platforms and market data; LME connectivity.",
    ],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-python-elixir-adoption",
    title="Python and Elixir enterprise adoption",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2010,
    responsible=["architected"],
    summary="Introduced and standardized Python (2010) and Elixir (2017) in the enterprise stack.",
    bullets=[
        "Introduced and standardized Python (2010) and Elixir (2017) in the enterprise stack.",
        "Ran workshops on Elixir, Performance Python, distributed databases, blockchains, trading-system anatomy.",
    ],
    skills=["Python", "Elixir"],
    split_from="rbc-language-platform-adoption",
)
add(
    id="rbc-five-rings",
    title="Five Rings mentorship program",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2016,
    kind="ran",
    responsible=["run"],
    summary="Five Rings mentorship program fostering startup culture and technology leaders.",
    bullets=[
        "Established the Five Rings mentorship program developing future technology leaders.",
        "Alumni cited include one CEO, two MDs, four directors, and eight ADs.",
    ],
    impact=["people"],
    proof={
        "metrics": [
            {"label": "alumni_mds", "value": 2},
            {"label": "alumni_directors", "value": 4},
        ],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-ops-team-restructure",
    title="Ops team restructure — maintenance → startup-style delivery",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    kind="ran",
    responsible=["run"],
    summary="Restructured 160+ NA maintenance team toward startup-style delivery incl. Malaysia; +20% apps/services.",
    bullets=[
        "Restructured a siloed 160+ North America maintenance team into startup-style development including Malaysia LCCs.",
        "Increased the number of applications and services by 20%.",
    ],
    impact=["people", "platform"],
    proof={
        "metrics": [
            {"label": "headcount", "value": 160},
            {"label": "apps_services_increase_pct", "value": 20},
        ],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-llm-governance",
    title="Bank-wide LLM services with governance",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2024,
    responsible=["architected", "run"],
    summary="Bank-wide LLM services with full governance.",
    bullets=["Modernization program including bank-wide LLM services with full governance."],
    skills=["Python"],
    domain=["finance", "AI"],
)
add(
    id="rbc-cobol-genai-migration",
    title="COBOL/mainframe ledger & stored-proc GenAI migration",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2024,
    responsible=["architected"],
    summary="Migrating off COBOL/mainframe ledgers; GenAI to migrate ~27k stored procedures.",
    bullets=[
        "Program work migrating off COBOL/mainframe-based ledgers.",
        "Using GenAI to migrate ~27k stored procedures.",
    ],
    skills=["Python"],
    domain=["finance", "AI"],
    proof={
        "metrics": [{"label": "stored_procedures", "value": 27000}],
        "links": [],
        "source": "job",
    },
)
add(
    id="rbc-usct-cross-border",
    title="USCT and cross-border payments programs",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2023,
    kind="ran",
    responsible=["run", "architected"],
    summary="USCT and cross-border payments programs (with SWIFT MX and T+1).",
    bullets=[
        "Managed and developed programs for USCT, cross-border payments, SWIFT MX, and T+1.",
    ],
)
add(
    id="rbc-agentic-workflow",
    title="Agentic service workflow service",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2024,
    responsible=["architected", "run"],
    summary="Agentic Service workflow service for trade operations shared infrastructure.",
    bullets=["Built and owned Agentic Service workflow service for trade operations."],
    skills=["Python"],
    domain=["finance", "AI"],
)
add(
    id="rbc-cm-virtual-accounts",
    title="Cash Management — virtual accounts & liquidity",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2020,
    end=2023,
    responsible=["built", "architected"],
    summary="Virtual accounts and liquidity management on the 5th-generation cash-management core.",
    bullets=["Built cash-management core including virtual accounts and liquidity management."],
    skills=["Elixir", "Rust", "Python"],
    split_from="rbc-cash-management-bank",
)
add(
    id="rbc-cm-payment-rails",
    title="Cash Management — payment manager & rails",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2020,
    end=2023,
    responsible=["built", "architected"],
    summary="Payment manager and rails for the transactional cash-management bank.",
    bullets=["Built payment manager/rails for the cash-management transactional bank."],
    skills=["Elixir", "Rust", "Python"],
    split_from="rbc-cash-management-bank",
)
add(
    id="rbc-cm-kyc-kyb",
    title="Cash Management — KYC/KYB, evidence & document store",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2020,
    end=2023,
    responsible=["built", "architected"],
    summary="CMS KYC/KYB plus evidence and document store; ERP integrations.",
    bullets=[
        "Built CMS KYC/KYB, evidence and document store, and ERP integrations for the cash-management bank.",
    ],
    skills=["Elixir", "Python"],
    split_from="rbc-cash-management-bank",
)
add(
    id="rbc-cm-blockchain-ledger",
    title="Cash Management — blockchain ledger accounting",
    client="RBC CM",
    org="RBC Capital Markets",
    job="rbc-cm",
    start=2020,
    end=2023,
    responsible=["architected"],
    summary="Core accounting on blockchain for the transactional bank; tholos-pq on the ledger.",
    bullets=[
        "Used blockchain for core accounting on the transactional cash-management bank.",
        "Used tholos-pq on the ledger.",
    ],
    skills=["Elixir", "Rust"],
    domain=["finance", "crypto"],
    split_from="rbc-cash-management-bank",
)

# Fix munis duplicate id while regenerating review
# (handled separately below)

# =============================================================================
# Split fat pre-RBC atoms + missing old-resume employers
# =============================================================================

# --- NYSE splits ---
for spec in [
    dict(
        id="nyse-market-surveillance",
        title="NYSE market surveillance — Python log analyzer & Java browser",
        start=1997,
        end=2004,
        summary="Python log-analyzer framework and Java log browser with embedded Python on trading-floor logs.",
        bullets=[
            "Built a Python log-analyzer framework for ad-hoc data mining, querying, and alarms on large/binary NYSE floor logs.",
            "Built a Java log browser with built-in Python scripting (WebSphere/J2EE/EncXML/SWIG).",
        ],
        skills=["Python", "Java"],
    ),
    dict(
        id="nyse-market-share",
        title="NYSE Market Share service into Specialist Portfolio",
        start=1997,
        end=2004,
        summary="Oracle→Specialist Portfolio market-share XML-RPC service; <1 month turnaround for Grasso ask.",
        bullets=[
            "Server collecting market-share data from Oracle and publishing into Specialist Portfolio (XML-RPC, PSO, Python, SWIG, C++, Tandem).",
            "High-profile demand from Mr. Grasso; turnaround less than one month.",
        ],
        skills=["Python", "C++"],
        proof={
            "metrics": [{"label": "turnaround", "value": "<1 month"}],
            "links": [],
            "source": "job",
        },
    ),
    dict(
        id="nyse-stock-info-server",
        title="NYSE Stock Information Server (pub/sub)",
        start=1997,
        end=2004,
        summary="Pub/sub stock-information server with XML-RPC/SQL subscribe and Tandem protocol bridge.",
        bullets=[
            "Pub/sub of stock information; clients subscribe with XML-RPC and SQL; publish over XML-RPC or HTTP.",
            "SWIG/C++ extended Python to subscribe to a bespoke Tandem protocol.",
        ],
        skills=["Python", "C++"],
    ),
    dict(
        id="nyse-member-firm-regulatory",
        title="NYSE Member Firm Regulatory Service — first XML feed",
        start=1997,
        end=2004,
        summary="Near-real-time XML feed of specialist-firm positions; first NYSE XML service.",
        bullets=[
            "Near-real-time XML feed of specialist-firm positions to the member-firm regulatory body.",
            "First NYSE XML service.",
        ],
        skills=["Python", "Java"],
    ),
    dict(
        id="nyse-specialist-portfolio",
        title="NYSE Specialist Portfolio — Swing client & trade details",
        start=1997,
        end=2004,
        summary="Swing Specialist Portfolio client with trade-detail mining and manual trades.",
        bullets=[
            "Designed/developed Python server feed, Java data model, GUI parts, Swing optimizations and printing; Web Start-ready plug-in.",
            "Added trade details for mining principal trades plus editing and manual trade entry.",
        ],
        skills=["Python", "Java", "C++"],
    ),
    dict(
        id="nyse-sec-supervision",
        title="NYSE/SEC event-sourced trader supervision",
        start=1997,
        end=2004,
        summary="Event-sourced rules-based trader supervision for the SEC.",
        bullets=[
            "Built event-sourced rules-based trader supervision for SEC (cited on résumé-2025 as NYSE/SEC/SIAC work).",
            "Related claim on bio materials: SEC trading compliance monitoring associated with prosecutions/convictions — verify before citing externally.",
        ],
        skills=["Python"],
        status="new-verify-claim",
    ),
    dict(
        id="nyse-web-trading",
        title="NYSE first web-based trading / specialist service",
        start=1997,
        end=2004,
        summary="First web-based trading service for the NYSE; early Python production finance system.",
        bullets=[
            "Built specialist trading systems including the first web-based trading service for the NYSE.",
            "Possibly the first financial production system written in Python.",
        ],
        skills=["Python"],
    ),
]:
    add(
        client="NYSE/SIAC",
        org="NYSE/SIAC",
        job="nyse-siac",
        domain=["finance", "trading"],
        split_from="nyse-surveillance-python",
        from_source="old_resumes",
        **spec,
    )

# --- ICAP splits ---
for spec in [
    dict(
        id="icap-brokertec-swing",
        title="BrokerTec fixed-income trading app (Java/Swing)",
        summary="Mainstream BrokerTec app with Random Walk; joystick trading, bulk orders, anonymous workup.",
        bullets=[
            "With Random Walk: Java 1.4→1.5 migration; joystick trading, quick order entry, net-position/P&L, batch/bulk orders, anonymous workup.",
        ],
        skills=["Java", "C++"],
    ),
    dict(
        id="icap-iconnect",
        title="BrokerTec iConnect conversion",
        summary="Converted main trading platform to use iConnect.",
        bullets=["Converted the main trading platform to iConnect (Java, SWIG, C++)."],
        skills=["Java", "C++"],
    ),
    dict(
        id="icap-emerging-markets-web",
        title="BrokerTec lightweight emerging-markets web trading",
        summary="Sub-10 MB web client for actives, repos, CDs, mortgages.",
        bullets=[
            "Web client for actives, repos, CDs, and mortgages on a non-Swing GUI, running under 10 MB.",
        ],
        skills=["Java"],
    ),
    dict(
        id="icap-gui-framework",
        title="Lightweight GUI framework for trading systems",
        summary="Config-driven trading UI framework; delivered a front-end in six weeks.",
        bullets=[
            "Screens/menus/panels/dialogs/columns/instruments specified in config and laid out dynamically.",
            "Used to deliver a trading front-end in six weeks.",
        ],
        skills=["Java"],
    ),
    dict(
        id="icap-blackberry-trading",
        title="BrokerTec/BlackBerry fixed-income trading PoC",
        summary="Spartan but fully functional real-time benchmarks-only handheld PoC.",
        bullets=[
            "Fully functional though Spartan real-time, benchmarks-only BlackBerry trading PoC (C++, WebSphere, J2EE).",
        ],
        skills=["C++", "Java"],
    ),
    dict(
        id="icap-jabber-backend",
        title="Distributed trading backend services (Jabber/async-j)",
        summary="Non-threaded high-performance fan-out for read-only/position screens.",
        bullets=[
            "Non-threaded Jabber/async-j/NIO services so hundreds of clients could share one guest account against BrokerTec.",
        ],
        skills=["Java"],
    ),
    dict(
        id="icap-conformance",
        title="Market conformance analysis tools",
        summary="Market conformance analysis and monitoring tools.",
        bullets=[
            "Designed market-conformance analysis and monitoring tools (Python, iLabs, WxWindows).",
        ],
        skills=["Python"],
    ),
]:
    add(
        client="ICAP",
        org="ICAP",
        job="icap",
        start=2004,
        end=2006,
        domain=["finance", "trading"],
        split_from="icap-fixed-income",
        from_source="old_resumes",
        **spec,
    )

# --- JPM Athena splits ---
for spec in [
    dict(
        id="jpm-trade-feed-framework",
        title="Athena energy trade-feed framework",
        summary="C/Python framework collecting, filtering, processing energy deals into Athena.",
        bullets=[
            "Built a C/Python trade-feed framework that collected, filtered, and processed deals into Athena.",
        ],
        skills=["C", "Python"],
    ),
    dict(
        id="jpm-cme-fix",
        title="CME FIX gateway to Athena",
        summary="CME FIX gateway to Athena trade feed for energy deals.",
        bullets=["Implemented a CME FIX gateway to the Athena trade feed for energy deals (Python)."],
        skills=["Python"],
    ),
    dict(
        id="jpm-ice-fix",
        title="ICE FIX gateway to Athena",
        summary="Enhanced ICE-to-Athena FIX trade feed for energy deals.",
        bullets=["Enhanced an existing ICE-to-Athena FIX trade feed for energy deals (Java, Python)."],
        skills=["Java", "Python"],
    ),
    dict(
        id="jpm-recon-framework",
        title="Energy feed reconciliation framework",
        summary="General reconciliation framework for booking systems / CME–ICE feeds.",
        bullets=[
            "Built reconciliation toolsets for the CME and ICE feeds; general reconciliation framework for booking systems.",
        ],
        skills=["Python"],
    ),
    dict(
        id="jpm-athena-profiler",
        title="Athena WxWindows/Python code profiler",
        summary="Profiler for performance and memory issues on the Athena stack.",
        bullets=[
            "Wrote a WxWindows/Python code profiler for performance and memory issues on Athena.",
        ],
        skills=["Python"],
    ),
    dict(
        id="jpm-energy-alerting",
        title="Energy feeds alert & logging framework",
        summary="Alert/logging framework combining useful parts of Nagios and Big Brother.",
        bullets=[
            "Delivered an alert and logging framework for all energy feeds (Nagios + Big Brother ideas).",
        ],
        skills=["Python"],
    ),
]:
    add(
        client="JPMorgan",
        org="JPMorgan",
        job="jpmorgan",
        start=2007,
        end=2007,
        domain=["finance", "trading"],
        split_from="jpm-athena-energy",
        from_source="old_resumes",
        **spec,
    )

add(
    id="jpm-gauss-cpr",
    title="GAUSS counterparty-risk performance (network & compute)",
    client="JPMorgan",
    org="JPMorgan",
    job="jpmorgan",
    start=2010,
    end=2011,
    summary="Network and computation performance improvements to counterparty risk system (GAUSS).",
    bullets=[
        "Contractor work on network and computation performance improvements to counterparty risk system (GAUSS).",
    ],
    skills=["C++", "Python"],
    from_source="old_resumes",
)

# --- CS splits ---
add(
    id="cs-openlink-pricing",
    title="Credit Suisse — OpenLink external pricing models",
    client="Credit Suisse",
    org="Credit Suisse",
    job="credit-suisse",
    start=2008,
    end=2010,
    summary="External pricing models integrated into OpenLink for complex commodities.",
    bullets=[
        "Integrated external pricing models into OpenLink for complex commodities trades.",
    ],
    skills=["C++", "Python"],
    split_from="cs-commodities-risk",
    from_source="old_resumes",
)
add(
    id="cs-trade-repo",
    title="Credit Suisse — central trade repository",
    client="Credit Suisse",
    org="Credit Suisse",
    job="credit-suisse",
    start=2008,
    end=2010,
    summary="Built central trade repository for commodities.",
    bullets=["Built central trade repository for commodities."],
    skills=["C++", "Python"],
    split_from="cs-commodities-risk",
    from_source="old_resumes",
)
add(
    id="cs-commodities-market-data",
    title="Credit Suisse — commodities market data services",
    client="Credit Suisse",
    org="Credit Suisse",
    job="credit-suisse",
    start=2008,
    end=2010,
    summary="Market data services for commodities.",
    bullets=["Built market data services for commodities."],
    skills=["Python"],
    split_from="cs-commodities-risk",
    from_source="old_resumes",
)

# --- Zingy splits (major products) ---
for spec in [
    dict(
        id="zingy-mapquest",
        title="MapQuest Mobile — #1 US phone app",
        summary="MapQuest Mobile; ~30% US market; multi-stop routing, POI, Canada.",
        bullets=[
            "#1 selling phone app in the US (~30% market; Weather Channel ~5%).",
            "Major upgrade: multi-stop routing, points of interest, and Canada (Java, C++, J2ME, Python).",
        ],
        skills=["Java", "C++", "Python"],
        proof={
            "metrics": [{"label": "US_share_pct", "value": 30}],
            "links": [],
            "source": "job",
        },
    ),
    dict(
        id="zingy-vindigo",
        title="Vindigo City Guide — top-ten mobile",
        summary="Third-best US / #1 UK; banner ads ~$320K/month; PhoneScript rewrite and ports.",
        bullets=[
            "Third-best-selling US app and #1 in the UK; banner-ad upgrade ~$320K/month.",
            "Rewrote client in PhoneScript; ports to Windows Mobile, Palm OS, BlackBerry.",
        ],
        skills=["Java", "C++", "Python"],
        proof={
            "metrics": [{"label": "ads_usd_per_month", "value": 320000}],
            "links": [],
            "source": "job",
        },
    ),
    dict(
        id="zingy-moviegoer-flash",
        title="Moviegoer — first US mobile Flash app",
        summary="First US mobile Flash application; Verizon bestseller four months; 96+ feeds.",
        bullets=[
            "First US mobile Flash application (early Adobe seeding partner).",
            "Showtimes, images, trailers, reviews, maps on Python backend with 96+ data feeds; Verizon bestseller four consecutive months.",
        ],
        skills=["Python", "Flash"],
    ),
    dict(
        id="zingy-plaxo",
        title="Plaxo mobile sync",
        summary="On-the-go personal-content sync; ~800 new subscribers/day at launch.",
        bullets=[
            "Shipped on 38 Verizon (Brew/C++) and 37 Sprint/Cingular (J2ME) handsets; ~800 new subscribers/day after November launch.",
        ],
        skills=["Java", "C++", "Python"],
        proof={
            "metrics": [{"label": "signups_per_day", "value": 800}],
            "links": [],
            "source": "job",
        },
    ),
    dict(
        id="zingy-nbc-weather",
        title="NBC Weather Mobile",
        summary="Sprint/Cingular weather app with MNG radar maps and real-time alerts.",
        bullets=[
            "35+ MIDP handsets; MNG animated radar maps; real-time weather alerts; tabular screens for small Samsung devices.",
        ],
        skills=["Java"],
    ),
    dict(
        id="zingy-nyt-ebay",
        title="New York Times Mobile & eBay Mobile",
        summary="eBay’s first mobile app; NYT syndication workflow to carrier news decks.",
        bullets=[
            "eBay Mobile and New York Times Mobile Java clients.",
            "New syndication workflow so NYT news feeds could land on carrier news decks.",
        ],
        skills=["Java"],
    ),
    dict(
        id="zingy-games-cms",
        title="Mobile games CMS / high-score server",
        summary="Stackless Python high-score server/CMS; 4000K simultaneous players cited.",
        bullets=[
            "High-score server and CMS for mobile multiplayer/fantasy games in Stackless Python.",
            "Cited handling over 4000K simultaneous players; trial for later server work.",
        ],
        skills=["Python"],
        domain=["gaming", "telecom"],
    ),
    dict(
        id="zingy-async-backend",
        title="Zingy async-j NIO backend & IPAY billing",
        summary="New asynchronous Java NIO backend (async-j); IPAY billing integration.",
        bullets=[
            "Built a new backend server around async-j (Java NIO).",
            "Integrated the new version of IPAY billing system.",
        ],
        skills=["Java"],
    ),
]:
    add(
        client="Zingy",
        org="Zingy",
        job="zingy",
        start=2006,
        end=2007,
        domain=spec.pop("domain", ["telecom", "gaming"]),
        split_from="zingy-mobile",
        from_source="old_resumes",
        **spec,
    )

# --- Infinigon ---
add(
    id="infinigon-social-ml",
    title="Infinigon — social-media ML trading analytics",
    client="Infinigon",
    org="Infinigon",
    job="infinigon",
    start=2012,
    end=2015,
    responsible=["built", "architected"],
    summary="ML analytics platform using real-time data and social sentiment for trading strategies.",
    bullets=[
        "Architected and built a machine learning analytics platform using real-time data and social media sentiment for trading strategies.",
    ],
    skills=["Python"],
    domain=["finance", "AI"],
    from_source="old_resumes",
)

# --- Pre-RBC missing employers / projects from old resumes ---
add(
    id="cable-wireless-telecom",
    title="Cable & Wireless — telecom systems",
    client="Cable & Wireless",
    org="Cable & Wireless",
    job=None,
    start=None,
    summary="Telecom work listed on nomination “Before RBC” and stack enumerations.",
    bullets=["Telecom systems work at Cable & Wireless (listed on MD nomination materials)."],
    domain=["telecom"],
    status="new-thin-dates",
    from_source="screenshots",
    source="manual",
    prov_type="other",
)
# fix start required - use approximate or leave; yaml needs start. Use null carefully.
ATOMS[-1]["when"] = {"start": None, "end": None}

add(
    id="panasonic-rip-fax",
    title="Panasonic — Forth RIP engines & fax drivers",
    client="Panasonic",
    org="Panasonic",
    job=None,
    start=1988,
    end=1992,
    summary="Forth-based RIP engines for Panasonic laser printers; most fax-machine drivers.",
    bullets=[
        "Wrote Forth-based RIP engines for Panasonic laser printers.",
        "Wrote most of the drivers for their fax machines.",
    ],
    skills=["Forth", "C"],
    domain=["telecom"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="drake-av-router",
    title="Philip Drake — AV trunk line router (BBC)",
    client="Philip Drake Ltd",
    org="Philip Drake Ltd",
    job=None,
    start=1989,
    end=1989,
    role="Team leader",
    summary="AV trunk/audio line router for broadcasting studio control; later purchased by BBC.",
    bullets=[
        "Developed code handling trunk and audio lines for complex broadcasting studio control (68000 firmware + X-Windows config + TCP/IP control).",
        "System later purchased by BBC.",
    ],
    skills=["C"],
    domain=["telecom"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="bbc-video-routing",
    title="BBC — video routing switches",
    client="BBC",
    org="BBC",
    job=None,
    start=1989,
    end=1990,
    summary="Video routing switches for the BBC (bio / nomination Before RBC).",
    bullets=["Video routing switches for the BBC (cited in bio and nomination materials)."],
    domain=["telecom"],
    status="new-thin",
    from_source="old_resumes+screenshots",
    source="manual",
    prov_type="other",
)
add(
    id="honeywell-bull-telecommuting",
    title="Honeywell Bull — telecommuting / home-working system",
    client="Honeywell Bull",
    org="Honeywell Bull",
    job=None,
    start=1990,
    end=1990,
    role="Homework Manager / Project Manager",
    summary="Servers for home working, spares/parts inventory, support and maintenance.",
    bullets=[
        "Developed numerous servers for home working, spares & parts inventory, support and maintenance (C++, Unix, Internet).",
    ],
    skills=["C++"],
    domain=["telecom"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="multitone-paging",
    title="Multitone — paging server & signaling",
    client="Multitone",
    org="Multitone Plc",
    job=None,
    start=1984,
    end=1985,
    summary="Paging server and signaling software; protocol design participation.",
    bullets=[
        "Developed paging server and paging signaling software (Unix C, HP3000).",
        "Participated in the design of the protocols; also a database for Multitone cited in bio.",
    ],
    skills=["C"],
    domain=["telecom"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="austin-knight-accounting",
    title="Austin Knight — advertisement coupon accounting",
    client="Austin Knight",
    org="Austin Knight Plc",
    job=None,
    start=1987,
    end=1987,
    summary="Online advertisement coupon handling accounts system.",
    bullets=[
        "Online Advertisement Coupon handling accounts system (AT&T 3B, Unix C, Sybase, SQL).",
    ],
    skills=["C"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="handy-newton-minitel",
    title="Handy Software — Newton Minitel, browser, Smalltalk",
    client="Handy Software",
    org="Handy Software",
    job=None,
    start=1993,
    end=1993,
    role="Project Manager",
    summary="Minitel client, Lynx-style web/ftp/telnet/email/gopher/news clients, Newton Smalltalk.",
    bullets=[
        "Developed a Minitel client for Apple Newton.",
        "Designed/developed Lynx-style web browser, ftp, telnet, email (POP), gopher and news clients.",
        "Newton SmallTalk interpreter for Newton.",
    ],
    skills=["NewtonScript"],
    domain=["telecom"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="forsyth-darwin-beagle",
    title="Richard Forsyth — Darwin / Beagle genetic programming",
    client="Richard Forsyth",
    org="Richard Forsyth",
    job=None,
    start=1980,
    end=1984,
    summary="Darwin genetic programming framework and Beagle horse-racing ML; early AI poker.",
    bullets=[
        "Coded Darwin genetic programming framework — one of the first ML platforms.",
        "Beagle system used as an oracle on horse racing; also board poker with virtual AI players.",
    ],
    skills=["C"],
    domain=["AI", "gaming"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="uk-treasury-transputer-nn",
    title="UK Treasury — Occam neural net on Transputers",
    client="UK Treasury",
    org="United Kingdom Treasury",
    job=None,
    start=1980,
    end=1981,
    summary="Occam-based neural network on Transputers; FX forecast / statistical methods intern work.",
    bullets=[
        "Occam-based neural network on Transputers for the UK Treasury (bio).",
        "Intern: foreign-exchange forecast, statistical methods, trend analysis, EISPACK/Fourier matrix lib (FORTRAN).",
    ],
    skills=["Occam", "FORTRAN"],
    domain=["AI", "finance"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="startup-rip-engines",
    title="Startup — RIP engines for printer manufacturers",
    client=None,
    org="Independent",
    job=None,
    start=1985,
    end=1988,
    summary="Left Atari to create a startup specializing in RIP engines for printer manufacturers.",
    bullets=[
        "Created a startup specializing in RIP engines for printer manufacturers after Atari PC games.",
    ],
    skills=["C", "Forth"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="marita-webcheck",
    title="Marita Bank — WebCheck early cyber currency",
    client="Marita Bank",
    org="Marita Bank",
    job=None,
    start=1995,
    end=1995,
    summary="Early cyber currency WebCheck for Caesars internet-casino payments.",
    bullets=[
        "With Marita Bank developed WebCheck, an early cyber currency, so the Caesars casino could take online payments.",
    ],
    domain=["finance", "crypto"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
    split_from="caesars-internet-casino",
)
add(
    id="ilabs-workflow",
    title="iLabs — object-oriented workflow (39 Eindhoven patterns)",
    client=None,
    org="Independent",
    job=None,
    start=1994,
    end=2007,
    summary="OO workflow conforming to all 39 Eindhoven patterns; used at EP, NYSE, JPM.",
    bullets=[
        "Built iLabs, an object-oriented workflow system conforming to all 39 Eindhoven patterns.",
        "Used by European Parliament EPADES/SECTORS, NYSE compliance, and JPMorgan ICE & CME trade booking.",
    ],
    skills=["Python", "C++"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="async-j",
    title="async-j — Java NIO asynchat-style wrapper",
    client=None,
    org="Independent",
    job=None,
    start=2004,
    end=2007,
    summary="Wrapped Java NIO to behave like Python’s asynchat; used at ICAP/Zingy backends.",
    bullets=[
        "Took crippled Java NIO and wrapped it to behave like Python’s asynchat (async-j).",
        "Used for ICAP distributed trading services and Zingy’s asynchronous backend.",
    ],
    skills=["Java"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="visual-trading",
    title="VisualTrading — lightweight Java UI framework",
    client=None,
    org="Independent",
    job=None,
    start=2004,
    end=2006,
    summary="Lightweight Java UI framework for trading front-ends (ICAP era).",
    bullets=["Built VisualTrading, a lightweight Java UI framework for trading front-ends."],
    skills=["Java"],
    domain=["finance", "trading"],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="oss-anex",
    title="ANEX — cryptocurrency exchange",
    client=None,
    org="Independent",
    job=None,
    start=2014,
    end=None,
    kind="oss",
    summary="ANEX cryptocurrency exchange.",
    bullets=["Built ANEX, a cryptocurrency exchange."],
    domain=["crypto"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="oss-chromite",
    title="Chromite — Bancor-style commodity-backed crypto",
    client=None,
    org="Independent",
    job=None,
    start=2014,
    end=None,
    kind="oss",
    summary="Bancor-based crypto currency backed by chromium mine deposits.",
    bullets=[
        "Chromite: a Bancor-based crypto currency backed by chromium mine deposits in the Ring of Fire.",
    ],
    domain=["crypto"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="oss-echo-social",
    title="Echo — realtime social analytical engine",
    client=None,
    org="Independent",
    job=None,
    start=2012,
    end=None,
    kind="oss",
    summary="Stream-based realtime social analytical engine.",
    bullets=["Echo: a stream-based realtime social analytical engine."],
    domain=["AI"],
    skills=["Python"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="oss-tradesource",
    title="TradeSource — trade abstraction framework",
    client=None,
    org="Independent",
    job=None,
    start=2012,
    end=None,
    kind="oss",
    summary="Trade abstraction framework in Erlang and Python.",
    bullets=["TradeSource: a trade abstraction framework written in Erlang and Python."],
    skills=["Erlang", "Python"],
    domain=["finance", "trading"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="oss-marketsource",
    title="MarketSource — market data framework",
    client=None,
    org="Independent",
    job=None,
    start=2012,
    end=None,
    kind="oss",
    summary="Market data framework in Erlang and Python.",
    bullets=["MarketSource: a market data framework written in Erlang and Python."],
    skills=["Erlang", "Python"],
    domain=["finance", "trading"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="oss-hyperstate",
    title="HyperState — iPhone gaming framework",
    client=None,
    org="Independent",
    job=None,
    start=2008,
    end=None,
    kind="oss",
    summary="Gaming framework for the iPhone.",
    bullets=["HyperState: a gaming framework for the iPhone."],
    domain=["gaming"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="oss-audiobook-caissa",
    title="AudioBook framework & Caissa chess on iPhone",
    client=None,
    org="Independent",
    job=None,
    start=2008,
    end=None,
    kind="oss",
    summary="Audio-visual book framework for iPhone; on the team that first brought chess (Caissa) to iPhone.",
    bullets=[
        "AudioBook: an audio-visual book framework for the iPhone.",
        "On the team that were the first to bring chess (Caissa) to the iPhone.",
    ],
    domain=["gaming"],
    from_source="old_resumes",
    source="manual",
    prov_type="oss",
)
add(
    id="interest-missing-persons-register",
    title="Global missing persons register",
    client=None,
    org=None,
    job=None,
    start=1994,
    end=None,
    kind="interest",
    summary="First global missing register; commended by the European Parliament.",
    bullets=[
        "Created the first global missing register (commended by the European Parliament).",
    ],
    from_source="old_resumes",
    source="manual",
    prov_type="other",
)
add(
    id="bt-timeseries-db",
    title="BT — fast time-series database for telecom",
    client="British Telecom",
    org="British Telecom",
    job="british-telecom",
    start=1992,
    end=1992,
    summary="Fast time-series database for telecom at BT.",
    bullets=["Developed a fast time-series database for telecom for BT."],
    skills=["C"],
    domain=["telecom"],
    from_source="old_resumes",
)
add(
    id="bt-tcpip-router-os",
    title="BT — TCP/IP router OS (Hope prototype)",
    client="British Telecom",
    org="British Telecom",
    job="british-telecom",
    start=1992,
    end=1992,
    summary="TCP/IP router programming/configuration embedded software; Hope used to prototype.",
    bullets=[
        "TCP/IP Router OS — embedded router programming and configuration software; Hope used to prototype.",
    ],
    skills=["C++", "Hope"],
    domain=["telecom"],
    from_source="old_resumes",
)
add(
    id="ep-first-website",
    title="European Parliament — first official website",
    client="European Parliament",
    org="European Parliament",
    job="european-parliament",
    start=1993,
    end=1995,
    summary="European Parliament’s first official website (europarl.eu.int).",
    bullets=["Built the European Parliament’s first official website (Linux, C, Python, Apache)."],
    skills=["Python", "C"],
    from_source="old_resumes",
    split_from="ep-workflow",
)
add(
    id="apple-newton-smalltalk",
    title="Apple/Handy — Newton Smalltalk port",
    client="Apple",
    org="Apple",
    job="apple",
    start=1993,
    end=1993,
    summary="Ported Smalltalk to the Newton.",
    bullets=["NewtonSmalltalk — ported Smalltalk to the Newton."],
    skills=["NewtonScript", "Smalltalk"],
    from_source="old_resumes",
)
add(
    id="ferranti-satellite-comms",
    title="Ferranti — armored satellite communications",
    client="Ferranti",
    org="Ferranti",
    job="ferranti",
    start=1986,
    end=1986,
    summary="Armored comms satellite programming mainly in C and 68000.",
    bullets=["Armored communications satellite programming mainly in C and 68000 (CP/M)."],
    skills=["C"],
    domain=["defence", "telecom"],
    from_source="old_resumes",
)
add(
    id="westlb-swaptions-pricing",
    title="WestLB — maturity calculators / swaptions pricing",
    client="WestLB",
    org="WestLB",
    job="west-lb",
    start=1996,
    end=1996,
    summary="Maturity data calculators and swap/options pricing; Summit converters.",
    bullets=[
        "Development of maturity data calculators and swap/options pricing mechanisms (C++, Fame, Infinity, Smalltalk).",
        "Some work on Summit converters.",
    ],
    skills=["C++", "Smalltalk"],
    split_from="westlb-var",
    from_source="old_resumes",
)
add(
    id="symantec-eispack-linpack",
    title="Symantec/Zortech — EISPACK/LINPACK ports to C++/Ada",
    client="Symantec",
    org="Symantec (Zortech)",
    job="symantec-zortech",
    start=1992,
    end=1992,
    summary="Ported EISPACK and LINPACK to C++ and Ada; numeric libraries.",
    bullets=[
        "Ported EISPACK and LINPACK to C++ and Ada.",
        "Coded standard libraries for Walter Bright’s C++ distribution (bio).",
    ],
    skills=["C++", "Ada"],
    split_from="symantec-cpp-numeric",
    from_source="old_resumes",
)
add(
    id="unilever-fuzzy-or",
    title="Unilever — OR pallet packing & fuzzy-logic control",
    client="Unilever",
    org="Unilever",
    job="unilever",
    start=1982,
    end=1984,
    summary="Operational research pallet packing and fuzzy-logic control systems; robotics.",
    bullets=[
        "OR (pallet packing) and then fuzzy logic control systems for Unilever.",
        "Robotic control programming on PDP-11 FORTRAN.",
    ],
    skills=["FORTRAN"],
    domain=["robotics"],
    split_from="unilever-robotics",
    from_source="old_resumes",
)

# Fix cable-wireless when start — yaml null
for a in ATOMS:
    if a["id"] == "cable-wireless-telecom":
        a["when"] = {"start": None, "end": None}


def thin_umbrella(path_id: str, title: str, summary: str, bullets: list[str], **extra):
    """Rewrite an umbrella atom to a thin pointer after splits."""
    path = EXP / f"{path_id}.yaml"
    if not path.exists():
        return
    d = yaml.safe_load(path.read_text())
    d["title"] = title
    d["summary"] = summary
    d["bullets"] = bullets
    d["provenance"] = d.get("provenance") or {}
    d["provenance"]["last_verified"] = TODAY
    d["provenance"]["note"] = "Thinned after granular split; see child atoms + EXPERIENCES-REVIEW."
    for k, v in extra.items():
        d[k] = v
    dump_atom(d)


def fix_munis_id():
    path = EXP / "rbc-ml-pricing-munis.yaml"
    if not path.exists():
        return
    d = yaml.safe_load(path.read_text())
    if d.get("id") == "rbc-ml-pricing":
        d["id"] = "rbc-ml-pricing-munis"
        # rewrite under correct filename already
        dump_atom(d)


def main():
    written = []
    for a in ATOMS:
        meta_status = a.pop("_status", "new")
        meta_split = a.pop("_split_from", None)
        meta_src = a.pop("_source", "")
        # skip overwrite if somehow conflicting with carefully hand-tuned? always write new ids
        path = dump_atom(a)
        written.append((a["id"], meta_status, meta_split, meta_src, path.name))

    # Thin umbrellas
    thin_umbrella(
        "rbc-language-platform-adoption",
        "Language & platform engineering adoption (umbrella)",
        "Umbrella for Python/Elixir adoption and platform services — see granular child atoms.",
        [
            "See child atoms: rbc-python-elixir-adoption, rbc-sts, rbc-faas, rbc-sns, rbc-cmla, rbc-distributed-compute, rbc-trading-data-core, rbc-data-lake, rbc-tokenization-platform, rbc-frtb-aml, rbc-lme-openlink, and related STS products.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "rbc-faas-notification",
        "FaaS + SNS (umbrella)",
        "Umbrella — see rbc-faas and rbc-sns.",
        ["See child atoms rbc-faas and rbc-sns."],
        kind="job_role",
    )
    thin_umbrella(
        "rbc-shared-data-services",
        "Shared Data Services mandate (umbrella)",
        "Umbrella for discoverable data fabric — see granular child atoms.",
        [
            "See child atoms: rbc-data-transport, rbc-data-ingest, rbc-emds, rbc-sdi, rbc-rabacus, rbc-ml-platform, and related.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "rbc-shared-ops-services",
        "Shared Operations Services portfolio (umbrella)",
        "Umbrella for shared ops portfolio — see granular child atoms.",
        [
            "See child atoms: rbc-t1-infrastructure, rbc-trade-repository, rbc-sns, and related ops products.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "rbc-cash-management-bank",
        "Cash Management Bank — 5th-generation core (umbrella)",
        "Umbrella for transactional cash-management bank — see granular child atoms.",
        [
            "See child atoms: rbc-cm-virtual-accounts, rbc-cm-payment-rails, rbc-cm-kyc-kyb, rbc-cm-blockchain-ledger, rbc-iso-20022-mx.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "nyse-surveillance-python",
        "NYSE/SIAC front-end systems (umbrella)",
        "Umbrella for NYSE/SIAC specialist systems — see granular child atoms.",
        [
            "See child atoms: nyse-market-surveillance, nyse-market-share, nyse-stock-info-server, nyse-member-firm-regulatory, nyse-specialist-portfolio, nyse-web-trading, nyse-sec-supervision.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "icap-fixed-income",
        "ICAP BrokerTec front-end (umbrella)",
        "Umbrella for ICAP/BrokerTec front-end work — see granular child atoms.",
        [
            "See child atoms: icap-brokertec-swing, icap-iconnect, icap-emerging-markets-web, icap-gui-framework, icap-blackberry-trading, icap-jabber-backend, icap-conformance.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "jpm-athena-energy",
        "JPMorgan Athena energy (umbrella)",
        "Umbrella for Athena energy trade-feed work — see granular child atoms.",
        [
            "See child atoms: jpm-trade-feed-framework, jpm-cme-fix, jpm-ice-fix, jpm-recon-framework, jpm-athena-profiler, jpm-energy-alerting.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "zingy-mobile",
        "Zingy mobile portfolio (umbrella)",
        "Umbrella for Zingy mobile apps — see granular child atoms.",
        [
            "See child atoms: zingy-mapquest, zingy-vindigo, zingy-moviegoer-flash, zingy-plaxo, zingy-nbc-weather, zingy-nyt-ebay, zingy-games-cms, zingy-async-backend.",
        ],
        kind="job_role",
    )
    thin_umbrella(
        "cs-commodities-risk",
        "Credit Suisse commodities (umbrella)",
        "Umbrella for CS commodities work — see granular child atoms.",
        [
            "See child atoms: cs-openlink-pricing, cs-trade-repo, cs-commodities-market-data (plus original risk system narrative).",
        ],
        kind="job_role",
    )

    fix_munis_id()

    # Build review from ALL yaml files
    rows = []
    for path in sorted(EXP.glob("*.yaml")):
        d = yaml.safe_load(path.read_text()) or {}
        when = d.get("when") or {}
        resp = d.get("responsible") or []
        if isinstance(resp, str):
            resp = [resp]
        meta = next((w for w in written if w[0] == d.get("id")), None)
        status = "existing"
        split_from = ""
        source = "corpus"
        if meta:
            status, split_from, source = meta[1], meta[2] or "", meta[3]
        if d.get("provenance", {}).get("note", "").startswith("Thinned"):
            status = "thinned-umbrella"
        bullets = d.get("bullets") or []
        rows.append(
            {
                "id": d.get("id"),
                "status": status,
                "split_from": split_from or "",
                "source": source,
                "kind": d.get("kind"),
                "responsible": "|".join(resp),
                "client": d.get("client") or "",
                "org": d.get("org") or "",
                "title": d.get("title") or "",
                "start": when.get("start") if when.get("start") is not None else "",
                "end": when.get("end") if when.get("end") is not None else "",
                "summary": (d.get("summary") or "").replace("\n", " "),
                "bullet_count": len(bullets),
                "first_bullet": (bullets[0] if bullets else "").replace("\n", " "),
                "skills": "|".join(d.get("skills") or []),
                "domains": "|".join(d.get("domain") or []),
                "visibility": d.get("visibility") or "",
                "file": path.name,
            }
        )

    fields = list(rows[0].keys()) if rows else []
    with REVIEW_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    new_n = sum(1 for r in rows if r["status"].startswith("new"))
    thin_n = sum(1 for r in rows if r["status"] == "thinned-umbrella")
    existing_n = sum(1 for r in rows if r["status"] == "existing")

    lines = [
        "# Experiences review catalog",
        "",
        f"Generated `{TODAY}`. **{len(rows)}** atoms total — "
        f"**{new_n}** new/split, **{thin_n}** thinned umbrellas, **{existing_n}** unchanged existing.",
        "",
        "Machine-readable: [`EXPERIENCES-REVIEW.csv`](EXPERIENCES-REVIEW.csv) (open in Excel/Numbers).",
        "",
        "Sources for new atoms: `content/resume/screenshots` (OCR), "
        "`content/resume/old_resumes/resume-2025.txt`, "
        "`content/resume/old_resumes/resume-incomplete.txt`.",
        "",
        "Status legend:",
        "- `new` — added from screenshots/old resumes",
        "- `new-verify-claim` / `new-thin` / `new-thin-dates` — added but needs your confirmation",
        "- `thinned-umbrella` — parent kept as pointer after granular split",
        "- `existing` — already in corpus (may still need review)",
        "",
        "## New & split atoms",
        "",
        "| id | start | client | title | split_from | status |",
        "|----|-------|--------|-------|------------|--------|",
    ]
    for r in rows:
        if r["status"] == "existing":
            continue
        lines.append(
            f"| `{r['id']}` | {r['start']} | {r['client']} | {r['title']} | "
            f"{r['split_from'] or '—'} | {r['status']} |"
        )

    lines += [
        "",
        "## All atoms (compact)",
        "",
        "| id | start–end | client | kind | title |",
        "|----|-----------|--------|------|-------|",
    ]
    for r in rows:
        end = r["end"] or ""
        span = f"{r['start']}–{end}" if r["start"] != "" else f"?–{end}"
        lines.append(
            f"| `{r['id']}` | {span} | {r['client']} | {r['kind']} | {r['title']} |"
        )

    REVIEW_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {len(written)} new/split atoms")
    print(f"Review: {REVIEW_CSV} ({len(rows)} rows)")
    print(f"Review: {REVIEW_MD}")


if __name__ == "__main__":
    main()
