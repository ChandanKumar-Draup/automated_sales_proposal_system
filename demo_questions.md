# Demo Questions for Sales Proposal System

This document contains curated questions for demonstrating the Q&A functionality of the Automated Sales Proposal System.

---

## Quick Demo Questions (1-2 minutes)

These questions are ideal for quick demonstrations and will produce confident answers with clear source citations:

1. **What case studies do we have in the healthcare industry?**
2. **What security certifications and compliance standards do we meet?**
3. **What is our typical implementation timeline?**
4. **What integration capabilities do we have with ATS and HRIS systems?**
5. **What pricing models do we offer?**

---

## Industry-Specific Questions

### Healthcare Industry
1. What HIPAA compliance features do we provide?
2. How do we handle Protected Health Information (PHI)?
3. What healthcare system integrations do we support (Epic, Cerner, Meditech)?
4. What clinical competency tracking features do we offer?
5. How do we support Joint Commission and CMS regulatory reporting?
6. What workforce forecasting capabilities do we have for clinical specialties?
7. Can we track nursing certifications like RN, LPN, and NP credentials?

### Semiconductor/Technology Industry
1. What experience do we have with semiconductor companies?
2. What talent intelligence capabilities do we offer for tech companies?
3. How do we approach skills taxonomy for engineering roles?
4. What labor market analysis do we provide for semiconductor talent?
5. What case studies do we have with companies like ASM or ARM?

### Manufacturing Industry
1. What manufacturing clients have we worked with?
2. How do we approach skills architecture for manufacturing roles?
3. What workforce planning solutions do we offer for manufacturing?
4. What experience do we have with automotive companies like Denso?

### Financial Services/Insurance
1. What compliance features do we offer for financial services?
2. How do we handle SOC2 compliance requirements?
3. What audit logging and data encryption standards do we provide?
4. What experience do we have with insurance companies like Liberty Mutual?

### Government/Public Sector
1. What labor market analysis do we provide for government agencies?
2. What experience do we have with state-level workforce planning?

---

## Technical & Security Questions

1. What is our platform architecture (cloud vs on-premise)?
2. What data encryption standards do we use?
3. What audit logging capabilities do we provide?
4. How do we ensure data security and privacy?
5. What disaster recovery and backup procedures do we have?
6. What APIs do we provide for integration?
7. What HL7 and FHIR integration capabilities do we have?
8. How do we handle multi-tenant data isolation?

---

## Commercial & Pricing Questions

1. What pricing models do we offer for different organization sizes?
2. What's included in our base package versus premium features?
3. How do we structure enterprise licensing?
4. What support and SLA options are available?
5. What is the typical contract term?
6. Do we offer volume discounts for large implementations?

---

## Implementation & Support Questions

1. What is our typical implementation timeline for enterprise clients?
2. What training and onboarding do we provide?
3. What ongoing support options are available?
4. How do we handle change management during implementation?
5. What resources are required from the client during implementation?
6. What is our approach to data migration?

---

## Competitive & Value Questions

1. What are our key differentiators compared to competitors?
2. What ROI have our customers achieved?
3. What measurable outcomes can clients expect?
4. How do we compare to traditional workforce planning tools?
5. What makes our talent intelligence unique?

---

## Advanced Demo Scenarios

### Scenario 1: Healthcare System RFP
*Context: A large healthcare system with 5 hospitals is evaluating vendors*

Questions to ask in sequence:
1. "What HIPAA compliance and BAA capabilities do we offer?"
2. "How do we integrate with Epic and Cerner systems?"
3. "What clinical workforce analytics do we provide?"
4. "What is our implementation timeline for a multi-hospital system?"

### Scenario 2: Tech Company Scaling
*Context: A technology company scaling from 50 to 200 engineers*

Questions to ask in sequence:
1. "What talent intelligence do we provide for engineering roles?"
2. "How do we approach skills taxonomy for technical positions?"
3. "What competitive intelligence can we provide on tech talent?"
4. "What pricing model works best for a growing tech company?"

### Scenario 3: Manufacturing Workforce Planning
*Context: An automotive manufacturer planning workforce transformation*

Questions to ask in sequence:
1. "What experience do we have with automotive companies?"
2. "How do we approach skills architecture for manufacturing?"
3. "What labor market analysis do we provide?"
4. "How do we support workforce forecasting?"

---

## Edge Case & Stress Test Questions

These questions test the system's ability to handle uncertainty:

1. **Out of scope**: "What CRM integrations do we offer?" (may have limited info)
2. **Broad query**: "Tell me everything about our platform" (tests summarization)
3. **Specific client**: "What did we propose to ASM?" (tests client-specific retrieval)
4. **Comparison**: "How do our healthcare features compare to our manufacturing features?"
5. **Historical**: "What was our first implementation in the semiconductor industry?"

---

## Batch Question Sets

### Set 1: Sales Team Onboarding (5 questions)
```json
{
  "questions": [
    "What are our key differentiators?",
    "What pricing models do we offer?",
    "What is our typical implementation timeline?",
    "What compliance certifications do we have?",
    "What ROI can clients expect?"
  ]
}
```

### Set 2: Technical Due Diligence (5 questions)
```json
{
  "questions": [
    "What is our platform architecture?",
    "What security certifications do we have?",
    "What integration capabilities do we offer?",
    "How do we handle data encryption?",
    "What APIs are available?"
  ]
}
```

### Set 3: Healthcare Prospect (5 questions)
```json
{
  "questions": [
    "What HIPAA compliance features do we offer?",
    "What healthcare system integrations do we support?",
    "What clinical workforce analytics do we provide?",
    "How do we handle PHI?",
    "What healthcare case studies do we have?"
  ]
}
```

---

## API Usage Examples

### Single Question
```bash
curl -X POST http://localhost:8000/api/v1/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What security certifications do we have?"}'
```

### Question with Context
```bash
curl -X POST http://localhost:8000/api/v1/qa/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What compliance features do we offer?",
    "context": "Prospect is a healthcare company concerned about HIPAA",
    "top_k": 5
  }'
```

### Batch Questions
```bash
curl -X POST http://localhost:8000/api/v1/qa/batch \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "What is our pricing model?",
      "What is our implementation timeline?",
      "What support options do we offer?"
    ]
  }'
```

---

## Expected Response Quality

### High Confidence (0.8+)
- Questions about compliance certifications
- Questions about integration capabilities
- Questions about pricing models
- Client-specific case studies

### Medium Confidence (0.5-0.8)
- Cross-industry comparisons
- Broad capability questions
- Historical questions

### Lower Confidence (<0.5)
- Questions outside the knowledge base scope
- Very specific technical details not in documents
- Future roadmap questions

---

## Tips for Effective Demos

1. **Start with high-confidence questions** to show the system working well
2. **Use industry-specific questions** when demoing to prospects in that industry
3. **Show source citations** to demonstrate transparency and trustworthiness
4. **Compare confidence scores** between different types of questions
5. **Use batch questions** to show efficiency for repetitive tasks
6. **Add context** to questions when relevant for better answers
