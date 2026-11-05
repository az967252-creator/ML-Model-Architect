# Requirements — Delivery Delay Prediction

## Goals
### Goal 1: Predict Delivery Delays
- What: Predict if a shipment will be delayed by more than 1 day.
- Decision supported: Customer support team sends proactive apologies and discount codes.
- Success metric: Increase CSAT (Customer Satisfaction) by 5% in 3 months.
- Error cost: False Positive is better than False Negative (missing a delayed shipment angers customers more).

## Requirements
- Data: Historical shipment logs (last 2 years) from the CRM.
- Features: Weather data, carrier history, distance.
