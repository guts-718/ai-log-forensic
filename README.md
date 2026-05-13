# Behavioral Anomaly Detection System (CERT Dataset)

## Overview
This project implements a full-stack behavioral anomaly detection system using the CERT insider threat dataset. The system evolves from rule-based detection to machine learning and finally prepares for deep learning (LSTM) modeling. The core objective is to detect anomalous user behavior by combining temporal, sequential, and user-specific contextual signals.

## Problem Statement
Traditional anomaly detection approaches either rely purely on static rules or purely on statistical models. Both approaches have limitations:
- Rules lack generalization
- ML models without context misclassify behavior
- Sequence information is often ignored
- User-specific behavior patterns are not modeled

This project addresses all of these issues step-by-step.

---

## Phase 1: Data Ingestion and Preprocessing

### Dataset
CERT Insider Threat Dataset (subset used due to resource constraints)

### Challenges
- Large dataset (GB scale)
- Limited local storage
- Need for fast iteration

### Solution
- Selected top N users (initially 5 → later scaled to 50)
- Built ingestion pipeline to parse logs into normalized event format

### Event Schema
```
{
    timestamp,
    user,
    event_type (logon, file, email, device),
    metadata
}
```

---

## Phase 2: Rule-Based Detection Engine

### Categories Implemented
- authentication
- data_access
- data_exfiltration
- network_anomaly
- lateral_movement
- privilege_escalation
- device_anomaly
- behavior_anomaly
- brute_force

### Approach
- Window-based processing (time windows)
- Score-based anomaly detection
- Risk levels: LOW / MEDIUM / HIGH

### Challenges
- Rules were heuristic and arbitrary
- Generated noisy labels
- High bias

### Insight
Rules are useful for:
- bootstrapping labels
- initial detection
- explainability

---

## Phase 2.5: Calibration

### Improvements
- Threshold tuning
- False positive reduction
- Score normalization

---

## Phase 3: Feature Engineering (Critical Phase)

### Initial Problem
ML models were overfitting due to:
- direct rule leakage
- overly clean labels
- lack of temporal understanding

---

### Feature Categories Implemented

#### 1. Basic Counts
- event_count
- file_count
- email_count
- device_count
- logon_count

#### 2. Temporal Features
- window_duration
- activity_intensity
- avg_time_gap
- min_time_gap
- std_time_gap
- burst_ratio

#### 3. Distribution Features
- file_ratio
- email_ratio
- device_ratio

#### 4. Entropy
- event_entropy (behavior randomness)

#### 5. Sequence Features
- sequence_signature
- transition counts
- transition_diversity
- event_switch_rate

#### 6. Pattern Features
- file_then_device_proximity
- max_event_repeat

---

## Major Breakthrough: Baseline Deviation

### Problem
Model could not differentiate:
- normal high activity
- anomalous high activity

### Solution
User-specific baselines:

```
feature_dev = (current - avg) / std
```

### Features Added
- file_dev_norm
- email_dev_norm
- logon_dev_norm
- total_dev

### Impact
This was the single most important improvement.

---

## Phase 4: ML Modeling

### Models Used
- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting
- LightGBM

---

## Training Strategy

### Cross-User Split
- Train on subset of users
- Test on unseen users
- Prevents leakage

---

### Threshold Optimization

Instead of fixed threshold:
- Dynamic threshold search
- Optimized using F-beta (beta=2)

### Precision Constraint
- Avoid trivial high-recall low-precision models

---

## Key Challenges and Solutions

### 1. Label Leakage
Problem:
- Features encoded rules directly

Solution:
- Removed direct flags
- Kept indirect sequence patterns

---

### 2. Unrealistic Perfect Scores
Problem:
- 99% accuracy initially

Solution:
- Added noise
- Harder labeling
- Cross-user split

---

### 3. Imbalance
Problem:
- Few anomalies

Solution:
- class_weight
- scale_pos_weight

---

### 4. Threshold Sensitivity
Problem:
- Small changes caused large performance swings

Solution:
- Automated threshold search
- F-beta optimization

---

### 5. Model Collapse (All Anomaly / All Normal)
Solution:
- fallback threshold logic
- precision constraints

---

## Final Results

### Best Model: LightGBM

Precision: 0.76  
Recall: 0.83  
F1 Score: 0.79  
F2 Score: 0.81  

### Interpretation
- High recall ensures anomalies are detected
- Reasonable precision keeps false positives manageable
- Balanced tradeoff suitable for real systems

---

## Model Comparison

| Model | Precision | Recall | Behavior |
|------|----------|--------|---------|
| LR | Low | High | Overpredicts |
| DT | Low | High | Unstable |
| RF | Moderate | Moderate | Baseline |
| GB | High | High | Strong |
| LGBM | Best | Best | Final Model |

---

## Key Insights

1. Feature engineering > model choice
2. Baseline deviation is critical
3. Sequence information matters
4. Threshold tuning is essential
5. Evaluation metric defines behavior

---

## Current System Architecture

```
Logs → Parser → Event Store → Detection Engine
     → Feature Builder → ML Model → Prediction
```

---

## Next Phase (Planned)

### Deep Learning (LSTM)

Goal:
- Capture temporal dependencies
- Model sequences directly

Pipeline:
```
event sequences → LSTM → anomaly score
```

---

## Conclusion

This project evolved from:
- rule-based detection
→ feature-driven ML
→ behavior-aware anomaly detection

The final system is:
- robust
- realistic
- explainable
- extensible

---

## Author Notes

This project emphasizes:
- engineering rigor
- realistic evaluation
- iterative improvement
- system design thinking

It is not optimized for perfect scores but for:
- real-world applicability
- interpretability
- scalability


