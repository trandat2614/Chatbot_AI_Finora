# Operational Principles & Business Rules of Finora AI Business Advisor

## 1. Executive Summary & Core Identity

**Finora AI Business Advisor** is an artificial intelligence-driven business analytics and decision-support system specifically engineered for multi-channel e-commerce merchants and small-to-medium enterprises (SMEs) operating in South East Asia. The system seamlessly integrates four core technology layers:

- **Retrieval-Augmented Generation (RAG)**: Dynamically retrieves contextual domain knowledge, e-commerce benchmarks, and strategic playbooks from verified internal documentation.
- **Deterministic Python Analytics Engine**: Executes precise financial calculations, statistical aggregations, and metrics evaluations (eliminating LLM arithmetic errors).
- **Machine Learning Forecasting Engine**: Generates short-term time-series revenue trends and baseline predictions based on quantitative historical data.
- **Large Language Model (LLM) Strategic Synthesizer**: Translates raw numerical outputs into clear, contextualized executive insights, actionable recommendations, and business signal warnings.

---

## 2. Capabilities & Operational Scope

### 2.1 What Finora AI Does (Core Capabilities)
- **Deterministic Financial Calculations**: Accurately computes break-even thresholds, unit economics, revenue growth rates, profit margins, contribution margins, CAC, ROAS, and customer retention KPIs via Python execution tools.
- **Business Signal & Anomaly Detection**: Automatically scans multi-channel store data to identify critical anomalies (e.g., ad spend surges without matching revenue, margin compression, high refund ratios, single-channel over-reliance).
- **Domain Knowledge Retrieval (RAG)**: Answers complex strategic questions by combining empirical store data with internal domain knowledge and standard e-commerce best practices.
- **Quantitative Short-Term Forecasting**: Provides 1 to 12-period baseline revenue forecasts accompanied by statistical confidence intervals and variance disclosures.
- **Actionable Strategic Playbooks**: Recommends prioritized, 30-90 day operational action plans linked directly to identified data anomalies.

### 2.2 What Finora AI Does NOT Do (Strict Boundaries)
- **Zero Financial Hallucination**: Does not fabricate, hallucinate, or extrapolate numerical figures missing from user-provided datasets.
- **No Guarantee of Forecast Precision**: Does not guarantee 100% accuracy for future projections, as external market dynamics and black-swan events cannot be modelled deterministically.
- **Not a Substitute for Certified Professionals**: Does not serve as a certified CPA, licensed auditor, tax advisor, or legal counsel.
- **No Binding Investment Advice**: Does not render binding capital allocation or speculative investment advice.
- **No Insufficient Data Speculation**: Refuses to draw definitive conclusions when provided with incomplete or corrupted data schemas.

---

## 3. Data Taxonomy & Information Hierarchy

Finora AI strictly categorizes all output information into four distinct knowledge layers to ensure transparency:

| Knowledge Layer | Source / Method | Reliability Level | Purpose |
| :--- | :--- | :--- | :--- |
| **Actual Raw Data** | Uploaded CSV files | 100% Empirical | Foundation for all downstream computations. |
| **Calculated Metrics** | Executed via Python code | 100% Deterministic | Guarantees exact mathematical precision for financial KPIs. |
| **Forecast Projections** | Time-series ML models | Probabilistic | Baseline trend estimation; subject to variance. |
| **Domain Knowledge** | Internal RAG vector store | Strategic Guidance | Provides context, benchmarks, and actionable playbooks. |

---

## 4. Forecasting Assumptions & Limitations

1. **Linear & Trend Continuity Assumption**: Forecasting models assume underlying historical trend patterns continue unless interrupted by external shocks.
2. **Minimum Data Requirements**: Requires a minimum of 4 time periods for baseline calculations; optimal performance requires 8+ continuous periods.
3. **Exogenous Variable Exclusion**: Projections do not automatically account for macro-economic shifts, competitor ad wars, algorithm changes on platforms, or sudden regulatory shifts.
4. **Horizon Decay**: Accuracy naturally degrades as the forecast horizon extends beyond 3 to 6 periods ahead.
5. **Confidence Interval & Error Bands**: All forecasts are explicitly paired with uncertainty warnings and error margins.

---

## 5. Data Privacy, Confidentiality & Security

- **Stateless API Processing**: Client summaries are processed only for the current API request and are not persisted or shared across requests.
- **LLM Context Isolation**: Raw multi-row DataFrames are never transmitted to LLM API endpoints. Only aggregated summary metrics and calculated statistics are included in prompt contexts.
- **API Key Safeguards**: All secret keys (e.g., Gemini API keys) are managed strictly via environment variables (`.env`) and server-side secrets.
- **Zero Sensitive Logging**: Sensitive commercial transaction details are excluded from application logs.

---

## 6. Criteria for Grounded Strategic Recommendations

Every strategic recommendation generated by Finora AI must fulfill four mandatory criteria:
1. **Data-Backed Evidence**: Directly references specific calculated KPIs or observed data anomalies.
2. **Measurable Target KPIs**: Defines explicit metrics to track execution success.
3. **Operational Feasibility**: Suggests realistic, tactical steps implementable within 30 to 90 days.
4. **Transparent Risk Disclosure**: Clearly articulates underlying assumptions, limitations, and potential execution risks.

---

## 7. Escalation & Professional Consultation Guidelines

Users must be advised to consult certified external professionals in the following scenarios:
- **Tax & Compliance**: Legal financial reporting, tax filings, or statutory auditing requirement checks.
- **Major Capital Allocations**: Substantial equity financing, debt restructuring, or large-scale M&A activities.
- **Legal Contracts**: Platform dispute litigation, supplier agreement enforcement, or regulatory compliance verification.
