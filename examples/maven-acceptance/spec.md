# 虚构示例：订单到期取消

此文件仅用于演示映射与报告解析，不是团队真实业务需求，也未执行真实 Spring Boot 工程。

## User Scenarios & Testing

### User Story 1 - 到期处理

**Acceptance Scenarios**:

1. **AC-001**: **Given** 未支付订单达到已确认的到期时刻，**When** 执行取消任务，**Then** 订单被取消。
2. **AC-002**: **Given** 订单已支付，**When** 执行取消任务，**Then** 保持已支付状态。

## Requirements

- FR-001：处理到期且未支付的订单。
- FR-002：已支付订单不被到期任务取消。

## Success Criteria

- 两个验收场景的指定测试实际执行并通过；业务边界仅用于虚构样例。
