# ADR-0053: Predictive Maintenance Engine

**Date:** 2026-06-16  
**Status:** Accepted  
**Author:** GCDTP Platform Team

---

## Context

The GCDTP platform has evolved through multiple stages:

1. **Operational Twin** - Basic asset management
2. **Contextual Twin** - Semantic layer, timeline, logbook
3. **Agent Twin** - AI agents with human approval
4. **Predictive Twin** - Failure prediction and maintenance recommendations

This ADR defines the Predictive Maintenance Engine, which introduces deterministic failure probability calculations and maintenance recommendations.

## Decision

### Core Principle: Deterministic First, ML Later

We will implement predictive maintenance using **deterministic formulas** before considering machine learning approaches.

**Reasons:**
1. **Explainability** - Every prediction can be traced to specific factors
2. **Auditability** - Deterministic rules are easier to audit for compliance
3. **Debuggability** - When predictions are wrong, we know exactly why
4. **Simplicity** - Fewer dependencies, easier to maintain
5. **Trust** - Human operators can understand and validate predictions

### Failure Probability Formula

```
FP = 0.30 × health_degradation
   + 0.25 × active_events
   + 0.25 × measurement_anomalies
   + 0.20 × maintenance_age
```

Where:
- `health_degradation`: How much health has degraded from 100%
- `active_events`: Number of active events on the asset
- `measurement_anomalies`: Number of measurement anomalies
- `maintenance_age`: Days since last maintenance

### Risk Classification

| Probability | Risk Level | Action |
|------------|------------|--------|
| 0-25% | LOW | Continue monitoring |
| 26-50% | MEDIUM | Plan maintenance within 30 days |
| 51-75% | HIGH | Schedule maintenance within 7 days |
| 76-100% | CRITICAL | Emergency inspection |

## Technical Implementation

### Database Schema

```sql
-- maintenance_prediction: Stores prediction records
-- maintenance_history: Stores maintenance work history
```

### Models

- `MaintenancePrediction` - Prediction record with factor breakdown
- `MaintenanceHistory` - Maintenance work history

### Service

- `PredictiveMaintenanceService` - Core deterministic calculations
  - `calculate_failure_probability()` - Weighted formula
  - `predict_health()` - Linear projection
  - `classify_risk()` - Threshold-based classification
  - `recommend_action()` - Rule-based recommendations

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predictive/run/{asset_id}` | POST | Run prediction |
| `/predictive/{asset_id}` | GET | Get latest prediction |
| `/predictive/history/{asset_id}` | GET | Prediction history |
| `/predictive/high-risk` | GET | High-risk assets |
| `/predictive/recommendations` | GET | Maintenance recommendations |
| `/predictive/timeline/{asset_id}` | GET | Health projections |
| `/predictive/probability/{asset_id}` | GET | Detailed probability analysis |

## Explainability

Every prediction includes:

1. **Factor Breakdown**
   - Health degradation contribution
   - Active events contribution
   - Measurement anomalies contribution
   - Maintenance age contribution

2. **Confidence Score**
   - Based on data quality
   - Higher confidence when more data available

3. **Recommendation Reasoning**
   - Why this recommendation was made
   - What factors drove the decision

## Human Supervision

**Predictions are ADVISORY ONLY:**

- ❌ No automatic work order creation
- ❌ No automatic scheduling
- ❌ No autonomous actions
- ❌ No self-healing
- ❌ No agent execution

Human operators review predictions and decide on actions.

## Future Considerations

When deterministic models prove insufficient:

1. **Feature Engineering** - Add more factors to the formula
2. **Weighted Learning** - Adjust weights based on historical accuracy
3. **Time-Series Analysis** - Detect degradation patterns
4. **Bayesian Models** - Include uncertainty quantification
5. **ML (Last Resort)** - Only if deterministic models fail

### ML Checklist Before Using ML

- [ ] Deterministic model achieves <80% accuracy
- [ ] Sufficient labeled training data available
- [ ] Model explainability requirements met
- [ ] Regulatory compliance verified
- [ ] False positive/negative costs understood
- [ ] Monitoring and drift detection in place

## Constraints

### STRICTLY FORBIDDEN

- ❌ TensorFlow
- ❌ PyTorch
- ❌ sklearn
- ❌ XGBoost
- ❌ Any external ML library
- ❌ Neural networks
- ❌ LSTM/RNN
- ❌ Autonomous work orders
- ❌ Automatic scheduling
- ❌ Self-healing
- ❌ Agent execution for maintenance

## Consequences

### Positive

- Fully explainable predictions
- Easy to debug and validate
- Low computational overhead
- No ML infrastructure needed
- Fast iteration on rules

### Negative

- Limited predictive power
- Cannot detect complex patterns
- Manual rule maintenance
- May miss subtle correlations

## Metrics for Success

1. **Prediction Accuracy** - How often predictions match reality
2. **Explainability Score** - Can operators understand predictions
3. **Action Rate** - How many predictions lead to actions
4. **False Positive Rate** - Unnecessary maintenance triggered
5. **False Negative Rate** - Failures not predicted

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-06-16 | 1.0 | Initial version |

---

**End of ADR-0053**
