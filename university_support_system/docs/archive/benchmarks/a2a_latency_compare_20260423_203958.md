# A2A Latency Compare

- Timestamp: `20260423_203958`
- Questions: `Q4, Q5, Q6, Q23`
- Warmups: `0`
- Repeats: `1`
- Disable cache: `True`
- HTTP/In-process median ratio: `0.314`

## Summary

| Mode | Count | Avg ms | Median ms | Min ms | Max ms |
|------|-------|--------|-----------|--------|--------|
| http_a2a | 4 | 15463.8 | 15431.5 | 13625.5 | 17366.8 |
| inprocess | 4 | 53434.2 | 49183.7 | 12257.3 | 103112.0 |

## Runs

### http_a2a

- A2A diagnostics delta: queries=4, agent_tasks=7, agent_task_failures=0

- Q4: 13625.5 ms; departments=['academic_programs']; modes=['rag+llm']; sources=4
- Q5: 17366.8 ms; departments=['academic_programs', 'student_affairs', 'finance']; modes=['llm', 'rag+llm', 'vt']; sources=10
- Q6: 16040.6 ms; departments=['finance', 'academic_programs']; modes=['llm', 'vt', 'rag+llm']; sources=3
- Q23: 14822.4 ms; departments=['student_affairs']; modes=['rag+llm']; sources=5

### inprocess

- Q4: 103112.0 ms; departments=['academic_programs']; modes=['rag']; sources=3
- Q5: 85780.2 ms; departments=['academic_programs', 'student_affairs', 'finance']; modes=['rag', 'vt']; sources=9
- Q6: 12257.3 ms; departments=['finance']; modes=['vt']; sources=0
- Q23: 12587.1 ms; departments=['student_affairs']; modes=['rag']; sources=5
