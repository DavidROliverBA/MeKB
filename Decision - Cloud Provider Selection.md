---
type: Decision
title: Cloud Provider Selection
created: 2025-12-20
status: approved
tags: [topic/cloud, topic/infrastructure]

context: Need to choose a cloud provider for new platform
alternatives:
  - option: AWS
    pros: [mature, team expertise, good serverless]
    cons: [complex pricing, vendor lock-in]
  - option: Azure
    pros: [Microsoft integration, hybrid options]
    cons: [less team experience]
  - option: GCP
    pros: [good ML/AI, Kubernetes native]
    cons: [smaller ecosystem]

decision: AWS
reasoning: Team already has AWS experience, Lambda fits our serverless-first approach
trade_offs: [Accept some vendor lock-in for faster delivery]
deciders: [Engineering Team]
date_decided: 2025-12-20
verified: 2026-02-04
---

# Cloud Provider Selection

## Context

We needed to select a cloud provider for the new platform build. Key requirements:
- Serverless-first architecture
- Strong CI/CD integration
- Team can ramp up quickly

## Decision

**We chose AWS.**

## Reasoning

1. Team already has 3 engineers with AWS certifications
2. Lambda + API Gateway fits our serverless approach
3. Terraform modules already exist from previous projects

## Trade-offs Accepted

- Some vendor lock-in with Lambda-specific patterns
- AWS pricing complexity requires monitoring

## Review Notes

_Check back in 6 months to evaluate if this was the right call._
