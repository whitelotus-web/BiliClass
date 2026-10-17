"""Independent local key budgets, never the account's Cloud credit."""


def summarize(rows, budget):
    budget = max(1, min(500_000, int(budget)))
    legacy = {}
    output = []
    for row in rows:
        project = row['project']
        legacy[project] = max(legacy.get(project, 0), row.get('legacyUsed', 0))
        used = max(0, row.get('used', 0))
        reserved = used + max(0, row.get('carryover', 0))
        percent = min(100, round(reserved * 100 / budget))
        level = 'exhausted' if reserved >= budget else 'critical' if reserved * 100 >= budget * 95 else 'warning' if reserved * 100 >= budget * 80 else 'normal'
        blocked = bool(row.get('blocked'))
        output.append({'project': project, 'name': row.get('name', ''), 'used': used,
                       'keyCount': 1, 'remaining': max(0, budget-reserved),
                       'budget': budget, 'percent': percent, 'level': level, 'blocked': blocked,
                       'unverified': False})
    usable = [row for row in output if row['remaining'] and not row['blocked']]
    warning = not rows or not usable or any(row['level'] != 'normal' or row['blocked'] for row in output)
    return {'groups': output, 'used': sum(row['used'] for row in output),
            'remaining': sum(row['remaining'] for row in usable), 'budget': budget,
            'keyCount': len(rows), 'counterCount': len(output), 'groupCount': len(legacy),
            'legacyUsed': sum(legacy.values()), 'totalBudget': budget * len(output),
            'configured': bool(rows), 'available': bool(usable), 'warning': warning,
            'unverified': False,
            'status': 'Chưa có key' if not rows else 'Cần kiểm tra giới hạn/key' if not usable else
                      'Gần giới hạn đã đặt' if warning else 'Trong giới hạn đã đặt'}
