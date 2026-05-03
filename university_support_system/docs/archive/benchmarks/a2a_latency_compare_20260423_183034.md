# A2A Latency Compare

- Timestamp: `20260423_183034`
- Questions: `Q5`
- Warmups: `1`
- Repeats: `1`
- Disable cache: `True`
- HTTP/In-process median ratio: `0.182`

## Summary

| Mode | Count | Avg ms | Median ms | Min ms | Max ms |
|------|-------|--------|-----------|--------|--------|
| http_a2a | 1 | 7080.0 | 7080.0 | 7080.0 | 7080.0 |
| inprocess | 1 | 38910.6 | 38910.6 | 38910.6 | 38910.6 |

## Runs

### http_a2a

- A2A diagnostics delta: queries=1, agent_tasks=3, agent_task_failures=0

- Q5: 7080.0 ms; departments=['academic_programs', 'student_affairs', 'finance']; modes=['llm', 'rag+llm', 'vt']; sources=10

### inprocess

- Q5: 38910.6 ms; departments=['academic_programs', 'student_affairs', 'finance']; modes=['rag', 'vt']; sources=9
